from datetime import datetime
from typing import cast

from langchain_core.runnables import RunnableConfig, RunnableLambda

from matcher.configuration import Configuration
from matcher.state import MainGraphState
from matcher.sub_graph.decision.models import (
    Conclusion,
    Decision,
    DecisionType,
    Outcome,
)
from utils import get_prompt, init_model


async def node_compatibility_flag(
    state: MainGraphState, config: RunnableConfig
) -> MainGraphState:
    """Analyze the candidate's compatibility flag."""
    # Load configuration from the provided RunnableConfig
    configuration = Configuration.from_runnable_config(config)

    # Initialize the prompt
    prompt = get_prompt("candidate-compatibility-flag")

    # Initialize the model
    raw_model = init_model(configuration.reasoning_model)
    model = raw_model.with_structured_output(Decision)

    # Create the chain
    chain = cast(RunnableLambda, prompt | model)

    decision = cast(
        Decision,
        await chain.ainvoke(
            {
                "profile": state.profile.model_dump(mode="json"),
                "job_synthesis": state.job_synthesis,
                "system_time": datetime.now().strftime("%B %d, %Y (%Y-%m-%-d)"),
            }
        ),
    )

    # Update the decision type
    decision.type = DecisionType.COMPATIBILITY_FLAG

    # Create a state update dictionary
    state_update = {
        "decisions": [decision],
    }

    # Only update synthesis_overall if location check fails
    if decision.outcome.value == Outcome.REJECTED.value:
        state_update["conclusion"] = Conclusion(
            outcome=Outcome.REJECTED,
            explanation=f"Required compatibility flag not met: {decision.explanation}",
            summary=[
                "🚫 Compatibility flag not satisfied",
                "📍 Candidate compatibility flag incompatible with job requirements",
            ],
        )

    return state_update
