from typing import Literal, cast

from langchain import hub
from langchain_core.exceptions import LangChainException
from langchain_core.runnables import RunnableLambda
from langgraph.types import Command

from feeder.models.people_search_filter import ProfileLanguage
from feeder.models.raw_query import RawQuery
from feeder.utils.init_model import init_model
from src.feeder.state import OverallState
from src.feeder.utils.logger_setup import logger


async def generate_raw_query(
    state: OverallState,
) -> Command[Literal["generate_raw_query_target_language", "reprocess_raw_query"]]:
    """Generate a raw query based on the job offer description and query memory (if the first generation query failed in the optimization process).

    Args:
        state: The overall state containing the job offer description and query memory.

    Returns:
        A dictionary containing the generated raw query under the 'raw_query' key.
    """
    if not state.job_offer_description:
        logger.error("No job offer description provided in state")
        raise ValueError("No job offer description provided.")
    try:
        logger.info("Starting raw query generation")
        llm = init_model("openai/o3-mini")
        structured_llm = llm.with_structured_output(RawQuery)
        prompt = hub.pull("first_gen_json_object_prompt")
        chain = cast(RunnableLambda, prompt | structured_llm)

        res = cast(
            RawQuery,
            await chain.ainvoke(
                {
                    "job_offer_description": state.job_offer_description,
                    "query_memory": state.query_memory
                    or "",  # Use empty string if query_memory is None
                }
            ),
        )

        # Generate raw query in target language, if target language is not English
        if state.target_language != ProfileLanguage.ENGLISH:
            return Command(
                update={"json_object": res},
                goto="generate_raw_query_target_language",
            )
        else:
            return Command(update={"json_object": res}, goto="reprocess_raw_query")
    except LangChainException as e:
        logger.error("Error generating raw query: %s", e)
        raise e
    except Exception as e:
        logger.error("Error generating raw query: %s", e)
        raise e
