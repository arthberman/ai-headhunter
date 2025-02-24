from typing import cast

from langchain import hub
from langchain_core.runnables import RunnableLambda

from feeder.utils.init_model import init_model
from src.feeder.subgraph.process_in_job_titles.models.feedback_judge import (
    FeedbackResponse,
)
from src.feeder.subgraph.process_in_job_titles.state import NewJobTitlesSubgraphState
from src.feeder.utils.logger_setup import logger


async def judge_existing_job_title(
    state: NewJobTitlesSubgraphState,
) -> dict[str, FeedbackResponse]:
    """Judge of the quality of each job title in the existing job titles.

    LLM Processing:
    - Uses structured output to enforce feedback format

    FeedbackResponse Format:
    {
        "anomalies": [                # List of detected job title anomalies
            {
                "issue": str,         # One of: "Role Alignment Issue", "Market Usage Issue", "Other Issue"
                "title": str,         # The problematic job title
                "explanation": str    # Detailed explanation of why the title is problematic
            },
            ...
        ]
    }

    Example FeedbackResponse:
    {
        "anomalies": [
            {
                "issue": "Role Alignment Issue",
                "title": "Junior Developer",
                "explanation": "This title indicates junior level which doesn't match the senior position requirements"
            }
        ]
    }
    """
    try:
        logger.info("Judging existing in_job_titles")
        llm = init_model(
            "bedrock_converse/us.anthropic.claude-3-5-sonnet-20241022-v2:0"
        )
        structured_llm = llm.with_structured_output(FeedbackResponse)

        prompt = hub.pull("judge_existing_job_titles")

        chain = cast(RunnableLambda, prompt | structured_llm)
        res = cast(
            FeedbackResponse,
            await chain.ainvoke(
                {
                    "json_object": state.json_object,
                    "job_offer_description": state.job_offer_description,
                }
            ),
        )
        logger.info(f"Successfully judged existing in_job_titles: {res}")
        return {"feedback_judge": res}
    except Exception as e:
        logger.error(f"Error in judge_existing_job_title: {e}")
        raise e
