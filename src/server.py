import asyncio
import signal
from typing import Any, Dict

from bullmq import Job, Queue, Worker
from langchain_core.runnables import RunnableLambda

from matcher.graph import compile_graph
from matcher.models.career_path import CareerPathAnalysis
from matcher.models.job_offer import JobOffer
from matcher.models.profile import Profile
from matcher.models.scorecard import ListScoredCriterion, Scorecard
from matcher.state import MainGraphState
from parser.joboffer import parseJobOffer
from parser.profile import parseProfile
from parser.scorecard import parseScorecard
from utils.logger import setup_logger

logger = setup_logger()
matcherResultQueue = Queue("matcher-results")


async def process_parser(job: Job, job_token: str) -> Dict[str, Any]:
    match job.name:
        case "joboffer":
            return await process_parser_joboffer(job)
        case "scorecard":
            return await process_parser_scorecard(job)
        case _:
            logger.error(f"Unknown job type: {job.name}")
            raise ValueError(f"Unknown job type: {job.name}")


async def process_parser_joboffer(job: Job) -> Dict[str, Any]:
    """Process a job offer."""
    logger.info(f"Processing job offer {job.id}")
    try:
        chain = RunnableLambda(parseJobOffer)
        res: JobOffer = await chain.ainvoke(job.data)
        return res.json()
    except Exception as e:
        logger.error(f"Error processing job offer {job.id}: {str(e)}", exc_info=True)
        raise ValueError(f"Failed to process job offer: {str(e)}") from e


async def process_parser_scorecard(job: Job) -> Dict[str, Any]:
    """Parse a scorecard from a job offer"""
    logger.info(f"Parse a scorecard from a job offer, job id: {job.id}")
    try:
        chain = RunnableLambda(parseScorecard)
        res: Scorecard = await chain.ainvoke(job.data)
        return res.json()
    except Exception as e:
        logger.error(f"Error processing job offer {job.id}: {str(e)}", exc_info=True)
        raise ValueError(f"Failed to process job offer: {str(e)}") from e


async def process_matcher(job: Job, job_token: str) -> Dict[str, Any]:
    """Process a matcher job"""
    logger.info(f"Processing matcher job {job.id}")
    try:
        profile: Profile = parseProfile(job.data["profile"])
        job_offer: JobOffer = JobOffer(**job.data["jobOffer"])
        scorecard: Scorecard = Scorecard(**job.data["scorecard"])
        chain = compile_graph()

        res: MainGraphState = await chain.ainvoke(
            {"profile": profile, "job_offer": job_offer, "scorecard": scorecard}
        )
        final_res = {
            "career_path_analysis": CareerPathAnalysis.json(
                res["career_path_analysis"]
            ),
            "education_analysis": ListScoredCriterion.json(res["education_analysis"]),
            "experience_analysis": ListScoredCriterion.json(res["experience_analysis"]),
            "soft_skill_analysis": ListScoredCriterion.json(res["soft_skill_analysis"]),
            "hard_skill_analysis": ListScoredCriterion.json(res["hard_skill_analysis"]),
            "language_analysis": ListScoredCriterion.json(res["language_analysis"]),
        }
        await matcherResultQueue.add("result", final_res)
        logger.info(f"Finished processing matcher job {job.id}")
    except Exception as e:
        logger.error(f"Error processing job offer {job.id}: {str(e)}", exc_info=True)
        raise ValueError(f"Failed to process job offer: {str(e)}") from e


async def main():
    logger.info("up and running")

    # Create an event that will be triggered for shutdown
    shutdown_event = asyncio.Event()

    def signal_handler(signal, frame):
        logger.warning("Signal received, shutting down.")
        shutdown_event.set()

    # Assign signal handlers to SIGTERM and SIGINT
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)

    parserWorker = Worker("parser", process_parser)
    parserMatcher = Worker("matcher", process_matcher)

    # Wait until the shutdown event is set
    await shutdown_event.wait()

    # close the worker
    logger.warning("Cleaning up worker...")
    await parserWorker.close()
    await parserMatcher.close()
    logger.warning("Worker shut down successfully.")


if __name__ == "__main__":
    asyncio.run(main())
