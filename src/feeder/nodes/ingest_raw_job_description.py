from typing import cast

from langchain import hub
from langchain_core.exceptions import LangChainException
from langchain_core.runnables import RunnableLambda

from feeder.models.job_offer import JobOfferDescription
from src.feeder.state import OverallInputState
from src.feeder.utils.init_model import init_model
from src.feeder.utils.logger_setup import logger

PROMPT_NAME = "ingest_raw_job_description_prompt"


async def ingest_raw_job_description(
    state: OverallInputState,
) -> dict[str, JobOfferDescription]:
    """Ingest the raw job description and extract a structured job description.

    Args:
        state: The overall input state containing the raw job description.

    Returns:
        Dict containing the structured job description under 'job_offer_description' key.
    """
    if not state.raw_job_description:
        logger.error("No raw job description provided in state")
        raise ValueError("No raw job description provided.")

    try:
        logger.info("Processing raw job description")

        llm = init_model("openai/o3-mini", temperature=0.0)
        structured_llm = llm.with_structured_output(JobOfferDescription)
        prompt = hub.pull(PROMPT_NAME)
        chain = cast(RunnableLambda, prompt | structured_llm)

        logger.debug(
            "Processing raw job description of length: %d",
            len(state.raw_job_description),
        )
        res = cast(
            JobOfferDescription,
            await chain.ainvoke({"raw_job_description": state.raw_job_description}),
        )
        logger.info("Successfully processed raw job description")

        return {"job_offer_description": res}

    except LangChainException as e:
        logger.error(f"Failed to process raw job description: {str(e)}")
        raise

    except Exception as e:
        logger.error(
            f"Unexpected error while processing raw job description: {str(e)}",
        )
        raise
