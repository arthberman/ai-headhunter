from typing import Optional, cast

from utils import get_prompt
from langchain_core.runnables import Runnable, RunnableConfig

from scorecard.configuration import Configuration
from scorecard.models.synthesis import Synthesis
from scorecard.state import ScorecardGraphState
from utils import init_model


def node_synthesis(
    state: ScorecardGraphState, *, config: Optional[RunnableConfig] = None
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
                "raw_job_posting": state.raw_job_posting,
                "web_context": state.web_context,
                "human_context": (state.human_context or [])
                + (state.human_feedback or []),
                "generated_questions": state.generated_questions,
            }
        ),
    )
    return {"synthesis": synthesis}
