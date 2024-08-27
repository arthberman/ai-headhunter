import asyncio
import signal
import warnings
from parser.joboffer import parseJobOffer
from parser.profile import parseProfile
from parser.scorecard import parseScorecard
from typing import Any, Dict

from bullmq import Job, Queue, Worker
from langchain_core._api.beta_decorator import LangChainBetaWarning
from langchain_core.runnables import RunnableLambda

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
matcherResultQueue = Queue("matcher-results")


@log_process(logger)
async def process_parser(job: Job, job_token: str) -> Dict[str, Any]:
    match job.name:
        case "joboffer":
            return await process_parser_joboffer(job)
        case "scorecard":
            return await process_parser_scorecard(job)
        case _:
            logger.error(f"Unknown job type: {job.name}")
            raise ValueError(f"Unknown job type: {job.name}")


@log_process(logger)
async def process_parser_joboffer(job: Job) -> Dict[str, Any]:
    """Process a job offer."""
    try:
        chain = RunnableLambda(parseJobOffer)
        res: JobOffer = await chain.ainvoke(job.data)
        return res.json()
    except Exception as e:
        logger.error(f"Error processing job offer {job.id}: {str(e)}", exc_info=True)
        raise ValueError(f"Failed to process job offer: {str(e)}") from e


@log_process(logger)
async def process_parser_scorecard(job: Job) -> Dict[str, Any]:
    """Parse a scorecard from a job offer"""
    try:
        chain = RunnableLambda(parseScorecard)
        res: Scorecard = await chain.ainvoke(job.data)
        return res.json()
    except Exception as e:
        logger.error(f"Error processing job offer {job.id}: {str(e)}", exc_info=True)
        raise ValueError(f"Failed to process job offer: {str(e)}") from e


@log_process(logger)
async def process_matcher(job: Job, job_token: str) -> Dict[str, Any]:
    """Process a matcher job"""
    try:
        profile: Profile = parseProfile(job.data["profile"])
        job_offer: JobOffer = JobOffer(**job.data["jobOffer"])
        scorecard: Scorecard = Scorecard(**job.data["scorecard"])
        analysisId: str = job.data["analysisId"]
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
        final_res = {
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
        await matcherResultQueue.add("result", final_res)
    except Exception as e:
        logger.error(f"Error processing job offer {job.id}: {str(e)}", exc_info=True)
        raise ValueError(f"Failed to process job offer: {str(e)}") from e


async def main():
    # Create an event that will be triggered for shutdown
    shutdown_event = asyncio.Event()

    def signal_handler(signal, frame):
        logger.warning("Signal received, shutting down.")
        shutdown_event.set()

    # Assign signal handlers to SIGTERM and SIGINT
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)

    # Feel free to remove the connection parameter, if your redis runs on localhost
    try:
        parserWorker = Worker("parser", process_parser)
        parserMatcher = Worker("matcher", process_matcher)
        logger.info("up and running")
    except Exception as e:
        logger.error(f"Error creating workers: {str(e)}", exc_info=True)
        raise ValueError(f"Failed to create workers: {str(e)}") from e

    # Wait until the shutdown event is set
    await shutdown_event.wait()

    # close the worker
    logger.warning("Cleaning up workers...")
    await parserWorker.close()
    await parserMatcher.close()
    await matcherResultQueue.close()
    logger.warning("Workers shut down successfully.")


if __name__ == "__main__":
    asyncio.run(main())
