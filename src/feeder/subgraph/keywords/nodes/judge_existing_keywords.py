from typing import cast

from langchain import hub
from langchain_core.runnables import RunnableLambda

from feeder.utils.init_model import init_model
from src.feeder.subgraph.keywords.models.feedback_judge import FeedbackResponse
from src.feeder.subgraph.keywords.state import KeywordsState


async def judge_existing_keywords(
    state: KeywordsState,
) -> KeywordsState:
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
    llm = init_model("bedrock_converse/us.anthropic.claude-3-5-sonnet-20241022-v2:0")
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
    return {"feedback_judge": res}
