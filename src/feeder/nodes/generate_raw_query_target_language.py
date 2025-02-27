from typing import cast

from langchain import hub
from langchain_core.exceptions import LangChainException
from langchain_core.runnables import RunnableLambda

from feeder.models.raw_query import RawQuery
from feeder.state import OverallState
from feeder.utils.init_model import init_model
from src.feeder.utils.logger_setup import logger


async def generate_raw_query_target_language(
    state: OverallState,
) -> OverallState:
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
        logger.info(f"Starting raw query generation in {state.target_language} ")
        llm = init_model("openai/o3-mini")
        structured_llm = llm.with_structured_output(RawQuery)
        target_language_prompt = hub.pull("first_gen_french_json_object_prompt")
        target_language_chain = cast(
            RunnableLambda, target_language_prompt | structured_llm
        )
        res_target_language = cast(
            RawQuery,
            await target_language_chain.ainvoke(
                {"job_offer_description": state.job_offer_description},
            ),
        )

        # Merge original query with target language query
        res = state.json_object
        if not res:
            raise ValueError("No raw query provided.")
        else:
            logger.info("Merging original query with target language query")
            res.in_job_titles = list(
                set(res.in_job_titles + res_target_language.in_job_titles)
            )
            res.not_in_job_titles = list(
                set(res.not_in_job_titles + res_target_language.not_in_job_titles)
            )
            res.keywords = list(set(res.keywords + res_target_language.keywords))

            logger.debug(
                f"Generated raw query in {state.target_language} successfully: {res}"
            )

        return state
    except LangChainException as e:
        logger.error("Error generating raw query: %s", e)
        raise e
    except Exception as e:
        logger.error("Error generating raw query: %s", e)
        raise e
