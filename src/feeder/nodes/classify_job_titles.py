from typing import cast

from langchain import hub
from langchain_core.runnables import RunnableLambda

from feeder.models.job_titles_ranking import (
    JobTitlesRankings,
)
from src.feeder.state import OverallState
from src.feeder.utils.init_model import init_model


async def classify_job_titles(
    state: OverallState,
) -> OverallState:
    """Classify the "in job titles" list from the most common to the least common."""
    llm = init_model("bedrock_converse/us.anthropic.claude-3-5-sonnet-20241022-v2:0")
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
    return {"job_titles_classified": res}
