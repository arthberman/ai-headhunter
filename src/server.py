import os
import asyncio
import signal
import warnings
from typing import Any, Dict

from temporalio import activity, worker
from temporalio.client import Client
from langchain_core._api.beta_decorator import LangChainBetaWarning
from langchain_core.runnables import RunnableLambda

from parser.job_posting import parse_job_posting
from parser.scorecard import parse_scorecard
from parser.profile import parse_profile
from matcher.graph import compile_graph
from matcher.models.career_path import CareerPathAnalysis
from matcher.models.job_posting import JobPosting
from matcher.models.profile import Profile
from scorecard.models.scorecard import ListScoredCriterion, Scorecard
from matcher.state import MainGraphState
from utils.logger import setup_logger

from langgraph_sdk import get_client

# Ignore LangChainBetaWarning
warnings.filterwarnings("ignore", category=LangChainBetaWarning)

logger = setup_logger()

client = get_client(url=os.environ["LANGGRAPH_URL"])


@activity.defn(name="parse_job_posting")
async def activity_parse_job_posting(raw_job_posting: str) -> Dict[str, Any]:
    """Process a job posting."""
    try:
        chain = RunnableLambda(parse_job_posting)
        res: JobPosting = await chain.ainvoke(raw_job_posting)
        return res.json()
    except Exception as e:
        logger.error(f"Error processing job posting: {str(e)}", exc_info=True)
        raise ValueError(f"Failed to process job posting: {str(e)}") from e


@activity.defn(name="parse_scorecard")
async def activity_parse_scorecard(raw_job_posting: str) -> Dict[str, Any]:
    """Parse a scorecard from a job posting"""
    try:
        chain = RunnableLambda(parse_scorecard)
        res: Scorecard = await chain.ainvoke(raw_job_posting)
        return res.json()
    except Exception as e:
        logger.error(f"Error processing scorecard: {str(e)}", exc_info=True)
        raise ValueError(f"Failed to process scorecard: {str(e)}") from e


@activity.defn(name="parse_scorecard_graph")
async def activity_parse_scorecard_graph(raw_job_posting: str) -> Dict[str, Any]:
    """Parse a scorecard from a job posting"""
    try:
        print("Parsing scorecard graph")
        assistant = await client.assistants.create(graph_id="scorecard")
        thread = await client.threads.create()
        await client.runs.wait(
            assistant_id=assistant["assistant_id"],
            thread_id=thread["thread_id"],
            input={"raw_job_posting": raw_job_posting},
            interrupt_after=["generate_questions"],
        )
        print({"thread_id": thread["thread_id"]})
        return {"thread_id": thread["thread_id"]}
    except Exception as e:
        logger.error(f"Error processing scorecard: {str(e)}", exc_info=True)
        raise ValueError(f"Failed to process scorecard: {str(e)}") from e


@activity.defn(name="process_matcher")
async def activity_process_matcher(job_data: Dict[str, Any]) -> Dict[str, Any]:
    """Process a matcher job"""
    try:
        profile: Profile = parse_profile(job_data["profile"])
        jobPosting: JobPosting = JobPosting(**job_data["jobPosting"])
        scorecard: Scorecard = Scorecard(**job_data["scorecard"])
        analysisId: str = job_data["analysisId"]
        chain = compile_graph()

        res: MainGraphState = await chain.ainvoke(
            {
                "profile": profile,
                "jobPosting": jobPosting,
                "scorecard": scorecard,
                "analysisId": analysisId,
            },
            config={
                "run_id": analysisId,
                "run_name": f"matcher-{jobPosting.company.lower().replace(' ', '-')}-{profile.linkedin_id.lower().replace(' ', '-')}",
            },
        )

        return {
            "analysisId": analysisId,
            "finalScore": res["final_score"],
            "mustHaveScore": res["must_have_score"],
            "importantScore": res["important_score"],
            "niceToHaveMultiplier": res["nice_to_have_multiplier"],
            "careerPathAnalysis": (
                CareerPathAnalysis.json(res["career_path_analysis"])
                if res["career_path_analysis"] is not None
                else None
            ),
            "educationAnalysis": (
                ListScoredCriterion.json(res["education_analysis"])
                if res["education_analysis"] is not None
                else None
            ),
            "experienceAnalysis": (
                ListScoredCriterion.json(res["experience_analysis"])
                if res["experience_analysis"] is not None
                else None
            ),
            "softSkillAnalysis": (
                ListScoredCriterion.json(res["soft_skill_analysis"])
                if res["soft_skill_analysis"] is not None
                else None
            ),
            "hardSkillAnalysis": (
                ListScoredCriterion.json(res["hard_skill_analysis"])
                if res["hard_skill_analysis"] is not None
                else None
            ),
            "languageAnalysis": (
                ListScoredCriterion.json(res["language_analysis"])
                if res["language_analysis"] is not None
                else None
            ),
            "industryKnowledgeAnalysis": (
                ListScoredCriterion.json(res["industry_knowledge_analysis"])
                if res["industry_knowledge_analysis"] is not None
                else None
            ),
            "additionalQualificationAnalysis": (
                ListScoredCriterion.json(res["additional_qualification_analysis"])
                if res["additional_qualification_analysis"] is not None
                else None
            ),
        }
    except Exception as e:
        logger.error(f"Error processing matcher job: {str(e)}", exc_info=True)
        raise ValueError(f"Failed to process matcher job: {str(e)}") from e


async def run_worker():
    client = await Client.connect(
        target_host=os.environ["TEMPORAL_HOST_URL"],
        namespace=os.environ["TEMPORAL_NAMESPACE"],
        rpc_metadata={"temporal-namespace": os.environ["TEMPORAL_NAMESPACE"]},
        api_key=os.environ["TEMPORAL_API_KEY"],
        tls=True,
    )
    task_queue_matcher = "repio-intelligence-matcher"
    task_queue_parser = "repio-intelligence-parser"

    # Create an event to signal shutdown
    stop_event = asyncio.Event()

    def shutdown():
        logger.info("Shutting down worker...")
        stop_event.set()

    # Register signal handlers for graceful shutdown
    loop = asyncio.get_running_loop()
    loop.add_signal_handler(signal.SIGINT, shutdown)
    loop.add_signal_handler(signal.SIGTERM, shutdown)

    # Run workers
    async with (
        worker.Worker(
            client,
            task_queue=task_queue_matcher,
            activities=[
                activity_process_matcher,
            ],
            max_activities_per_second=1 / 60,
        ) as worker_1,
        worker.Worker(
            client,
            task_queue=task_queue_parser,
            activities=[
                activity_parse_job_posting,
                activity_parse_scorecard,
                activity_parse_scorecard_graph,
            ],
            max_task_queue_activities_per_second=2 / 60,
        ) as worker_2,
    ):
        logger.info(
            f"Worker 1 started on {task_queue_matcher} task queue. Ctrl+C to exit."
        )
        logger.info(
            f"Worker 2 started on {task_queue_parser} task queue. Ctrl+C to exit."
        )
        await stop_event.wait()  # Wait until the stop event is set
        logger.info("Workers stopped.")


if __name__ == "__main__":
    asyncio.run(run_worker())
