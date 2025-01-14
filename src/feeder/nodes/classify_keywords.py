from typing import cast

from langchain import hub
from langchain_core.runnables import RunnableLambda

from feeder.models.keywords_ranking import (
    KeywordsRankings,
)
from feeder.utils.init_model import init_model
from feeder.state import OverallState


def classify_keywords(
    state: OverallState,
) -> OverallState:
    """Classify the "keywords" list from the broadest keyword to the most specific according to a job offer description."""
    llm = init_model("bedrock_converse/us.anthropic.claude-3-5-sonnet-20241022-v2:0")
    structured_llm = llm.with_structured_output(KeywordsRankings)

    prompt = hub.pull("classify_keywords")
    chain = cast(RunnableLambda, prompt | structured_llm)
    res = cast(
        KeywordsRankings,
        chain.invoke(
            {
                "job_offer_description": state.job_offer_description,
                "keywords": state.json_object.keywords,
            }
        ),
    )

    keywords_dict = {
        "far": res.far if res.far else [],
        "near": res.near if res.near else [],
    }
    return {"keywords_classified": keywords_dict}
