from typing import cast

from langchain import hub
from langchain_core.runnables import RunnableLambda

from feeder.utils.init_model import init_model
from feeder.subgraph.in_job_titles.models.feedback_judge import (
    FeedbackResponse,
)
from feeder.subgraph.in_job_titles.state import NewJobTitlesSubgraphState


def judge_existing_job_title(
    state: NewJobTitlesSubgraphState,
) -> NewJobTitlesSubgraphState:
    """Judge of the quality of the job titles in the existing job titles."""

    llm = init_model("bedrock_converse/us.anthropic.claude-3-5-sonnet-20241022-v2:0")
    structured_llm = llm.with_structured_output(FeedbackResponse)

    prompt = hub.pull("judge_existing_job_titles")

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
