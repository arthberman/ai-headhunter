import asyncio
import warnings
from typing import Any, Dict

from temporalio import activity, worker
from temporalio.client import Client
from langchain_core._api.beta_decorator import LangChainBetaWarning
from langchain_core.runnables import RunnableLambda

from parser.joboffer import parseJobOffer
from parser.scorecard import parseScorecard
from parser.profile import parseProfile
from matcher.graph import compile_graph
from matcher.models.career_path import CareerPathAnalysis
from matcher.models.job_offer import JobOffer
from matcher.models.profile import Profile
from matcher.models.scorecard import ListScoredCriterion, Scorecard
from matcher.state import MainGraphState
from utils.logger import log_process, setup_logger

# Ignore LangChainBetaWarning
warnings.filterwarnings("ignore", category=LangChainBetaWarning)

logger = setup_logger()


@activity.defn(name="hello_world")
async def hello_world(name: str) -> str:
    """A simple activity for testing purposes."""
    message = f"Hello, {name}!"
    print(message)
    return message


# ... (keep the existing activity definitions) ...


@activity.defn(name="process_parser_joboffer")
@log_process(logger)
async def process_parser_joboffer(job_data: Dict[str, Any]) -> Dict[str, Any]:
    """Process a job offer."""
    try:
        chain = RunnableLambda(parseJobOffer)
        res: JobOffer = await chain.ainvoke(job_data)
        return res.json()
    except Exception as e:
        logger.error(f"Error processing job offer: {str(e)}", exc_info=True)
        raise ValueError(f"Failed to process job offer: {str(e)}") from e


@activity.defn(name="process_parser_scorecard")
@log_process(logger)
async def process_parser_scorecard(job_data: Dict[str, Any]) -> Dict[str, Any]:
    """Parse a scorecard from a job offer"""
    try:
        chain = RunnableLambda(parseScorecard)
        res: Scorecard = await chain.ainvoke(job_data)
        return res.json()
    except Exception as e:
        logger.error(f"Error processing scorecard: {str(e)}", exc_info=True)
        raise ValueError(f"Failed to process scorecard: {str(e)}") from e


@activity.defn(name="process_matcher")
@log_process(logger)
async def process_matcher(job_data: Dict[str, Any]) -> Dict[str, Any]:
    """Process a matcher job"""
    try:
        profile: Profile = parseProfile(job_data["profile"])
        job_offer: JobOffer = JobOffer(**job_data["jobOffer"])
        scorecard: Scorecard = Scorecard(**job_data["scorecard"])
        analysisId: str = job_data["analysisId"]
        chain = compile_graph()

        res: MainGraphState = await chain.ainvoke(
            {
                "profile": profile,
                "job_offer": job_offer,
                "scorecard": scorecard,
                "analysisId": analysisId,
            },
            config={
                "run_id": analysisId,
                "run_name": f"matcher-{job_offer.company.lower().replace(' ', '-')}-{job_offer.title.lower().replace(' ', '-')}",
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
        }
    except Exception as e:
        logger.error(f"Error processing matcher job: {str(e)}", exc_info=True)
        raise ValueError(f"Failed to process matcher job: {str(e)}") from e


async def run_worker():
    client = await Client.connect("localhost:7233")

    # Run the worker
    async with worker.Worker(
        client,
        task_queue="ai-processing",
        activities=[
            hello_world,
            process_parser_joboffer,
            process_parser_scorecard,
            process_matcher,
        ],
    ):
        logger.info("Worker started. Ctrl+C to exit.")
        await asyncio.Future()  # Run forever


if __name__ == "__main__":
    asyncio.run(run_worker())
