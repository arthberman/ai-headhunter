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
from utils.logger import setup_logger, log_process

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
            }
        )
        final_res = {
            "analysisId": analysisId,
            "careerPathAnalysis": CareerPathAnalysis.json(res["career_path_analysis"]),
            "educationAnalysis": ListScoredCriterion.json(res["education_analysis"]),
            "experienceAnalysis": ListScoredCriterion.json(res["experience_analysis"]),
            "softSkillAnalysis": ListScoredCriterion.json(res["soft_skill_analysis"]),
            "hardSkillAnalysis": ListScoredCriterion.json(res["hard_skill_analysis"]),
            "languageAnalysis": ListScoredCriterion.json(res["language_analysis"]),
        }
        await matcherResultQueue.add("result", final_res)
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

    try:
        # Wait until the shutdown event is set
        await shutdown_event.wait()
    finally:
        # close the workers
        logger.warning("Cleaning up workers...")
        await asyncio.gather(parserWorker.close(), parserMatcher.close())
        logger.warning("Workers shut down successfully.")

        # Close any remaining connections
        tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
        [task.cancel() for task in tasks]
        await asyncio.gather(*tasks, return_exceptions=True)

        # Optionally, you can add a small delay to allow for cleanup
        await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(main())
