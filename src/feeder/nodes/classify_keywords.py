from typing import cast

from langchain import hub
from langchain_core.exceptions import LangChainException
from langchain_core.runnables import RunnableLambda

from feeder.models.keywords_ranking import KeywordsRankings
from feeder.utils.init_model import init_model
from src.feeder.state import OverallState
from src.feeder.utils.logger_setup import logger


async def classify_keywords(
    state: OverallState,
) -> dict[str, KeywordsRankings]:
    """Classify the "keywords" list from the broadest keyword to the most specific according to a job offer description."""
    try:
        logger.info("Classifying keywords")
        llm = init_model(
            "bedrock_converse/us.anthropic.claude-3-5-sonnet-20241022-v2:0"
        )
        structured_llm = llm.with_structured_output(KeywordsRankings)

        prompt = hub.pull("classify_keywords")
        chain = cast(RunnableLambda, prompt | structured_llm)

        res = cast(
            KeywordsRankings,
            await chain.ainvoke(
                {
                    "job_offer_description": state.job_offer_description,
                    "keywords": state.json_object.keywords if state.json_object else [],
                }
            ),
        )
        logger.info(f"Keywords classified successfully: {res}")
        return {"keywords_classified": res}
    except LangChainException as e:
        logger.error(f"Error classifying keywords: {e}")
        raise e
    except Exception as e:
        logger.error(f"Error classifying keywords: {e}")
        raise e
