from typing import cast

from langchain import hub
from langchain_core.runnables import RunnableLambda

from feeder.utils.init_model import init_model
from feeder.subgraph.keywords.models.feedback_judge import FeedbackResponse
from feeder.subgraph.keywords.state import KeywordsState


def judge_existing_keywords(
    state: KeywordsState,
) -> KeywordsState:
    """Judge of the quality of the keywords in the keywords list."""
    llm = init_model("bedrock_converse/us.anthropic.claude-3-5-sonnet-20241022-v2:0")
    structured_llm = llm.with_structured_output(FeedbackResponse)

    prompt = hub.pull("judge_existing_keywords")

    chain = cast(RunnableLambda, prompt | structured_llm)
    res = cast(
        FeedbackResponse,
        chain.invoke(
            {
                "json_object": state.json_object,
                "job_offer_description": state.job_offer_description,
            }
        ),
    )
    return {"feedback_judge": res}
