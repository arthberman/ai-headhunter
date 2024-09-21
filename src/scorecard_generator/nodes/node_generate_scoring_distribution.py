from typing import List

from langchain import hub
from langchain.chat_models import init_chat_model

from scorecard_generator.models.scorecard import Scorecard
from scorecard_generator.state import ScorecardGraphState


def node_generate_scoring_distribution(
    state: ScorecardGraphState,
) -> ScorecardGraphState:
    prompt = hub.pull("parser-scorecard-scoring-distribution")

    model = init_chat_model(
        model="gpt-4o-2024-08-06", model_provider="openai", temperature=0
    ).with_structured_output(Scorecard)

    chain = prompt | model

    res: Scorecard = chain.invoke(
        {
            "scorecard": state.scorecard,
        }
    )

    return {"scorecard": res}
