from typing import cast

from langchain import hub
from langchain_core.runnables import RunnableLambda

from feeder.utils.init_model import init_model
from src.feeder.subgraph.process_keywords.models.feedback_judge import (
    FeedbackResponse,
)
from src.feeder.subgraph.process_keywords.state import KeywordsState
from src.feeder.utils.logger_setup import logger


async def judge_existing_keywords(
    state: KeywordsState,
) -> dict[str, FeedbackResponse]:
    """Judge of the quality of the keywords in the keywords list.

    LLM Processing:
    - Uses structured output to enforce feedback format

    FeedbackResponse Format:
    {
        "precise_keywords": [str],
        "broad_keywords": [str]
    }

    Example FeedbackResponse:
    {
        "precise_keywords": ["Node.js", "React", "TypeScript"],
        "broad_keywords": ["JavaScript", "Frontend", "Web Development"]
    }
    """
    try:
        logger.info("Judging existing keywords")
        llm = init_model(
            "bedrock_converse/us.anthropic.claude-3-5-sonnet-20241022-v2:0"
        )
        structured_llm = llm.with_structured_output(FeedbackResponse)
        prompt = hub.pull("judge_existing_keywords")
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
        logger.info("Successfully judged existing keywords")
        return {"feedback_judge": res}
    except Exception as e:
        logger.error(f"Error in judge_existing_keywords: {e}")
        raise e
