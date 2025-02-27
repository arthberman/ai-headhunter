from typing import cast

from langchain import hub
from langchain_core.exceptions import LangChainException
from langchain_core.runnables import RunnableLambda

from feeder.models.job_titles_ranking import (
    JobTitlesRankings,
)
from src.feeder.state import OverallState
from src.feeder.utils.init_model import init_model
from src.feeder.utils.logger_setup import logger


async def classify_job_titles(
    state: OverallState,
) -> dict[str, JobTitlesRankings]:
    """Classify the "in job titles" list from the most common to the least common."""
    try:
        logger.info("Classifying job titles")
        llm = init_model(
            "bedrock_converse/us.anthropic.claude-3-5-sonnet-20241022-v2:0"
        )
        structured_llm = llm.with_structured_output(JobTitlesRankings)

        prompt = hub.pull("classify_job_titles")
        chain = cast(RunnableLambda, prompt | structured_llm)
        res = cast(
            JobTitlesRankings,
            await chain.ainvoke(
                {
                    "json_object": state.json_object,
                    "job_offer_description": state.job_offer_description,
                }
            ),
        )
        logger.info(f"Job titles classified successfully: {res}")
        return {"job_titles_classified": res}
    except LangChainException as e:
        logger.error(f"Error classifying job titles: {e}")
        raise e
    except Exception as e:
        logger.error(f"Error classifying job titles: {e}")
        raise e
