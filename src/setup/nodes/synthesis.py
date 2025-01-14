from typing import cast

from langchain_core.runnables import Runnable, RunnableConfig

from setup.configuration import Configuration
from setup.models.synthesis import Synthesis
from setup.state import ScorecardGraphState
from utils import get_prompt, init_model


def node_synthesis(
    state: ScorecardGraphState, *, config: RunnableConfig
) -> ScorecardGraphState:
    """Synthesize the scorecard."""
    configuration = Configuration.from_runnable_config(config)

    raw_model = init_model(configuration.default_model)

    model = raw_model.with_structured_output(Synthesis)
    prompt = get_prompt("generate-scorecard-synthesis")

    chain = cast(Runnable, prompt | model)
    synthesis = cast(
        Synthesis,
        chain.invoke(
            {
                "resources": state.resources,
                "questions": state.questions.model_dump(mode="json"),
            }
        ),
    )
    return {"synthesis": synthesis}
