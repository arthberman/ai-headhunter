"""Define the node for the scorecard synthesis."""

from langchain import hub
from langchain.chat_models import init_chat_model
from typing import cast

from scorecard_generator.state import ScorecardGraphState
from scorecard_generator.models.synthesis import Synthesis


def node_synthesis(state: ScorecardGraphState) -> ScorecardGraphState:
    model = init_chat_model(
        model="gpt-4o-2024-08-06", model_provider="openai", temperature=0
    )
    structured_model = model.with_structured_output(Synthesis)
    prompt = hub.pull("scorecard-synthesis")

    chain = prompt | structured_model
    synthesis = cast(Synthesis, chain.invoke(state))
    return {"synthesis": synthesis}
