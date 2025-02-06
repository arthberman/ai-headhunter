from datetime import datetime
from typing import cast

from langchain_core.runnables import RunnableConfig, RunnableLambda

from matcher.configuration import Configuration
from matcher.state import MainGraphState
from matcher.sub_graph.decision.models import IntentToMove
from utils import get_prompt, init_model


async def node_synthetize_intent(state: MainGraphState, config: RunnableConfig):
    """Synthesize the intent of the profile."""
    # Load configuration from the provided RunnableConfig
    configuration = Configuration.from_runnable_config(config)

    # Initialize the prompt
    prompt = get_prompt("candidate-analysis-intent")

    # Initialize the model
    raw_model = init_model(configuration.synthesis_model)
    model = raw_model.with_structured_output(IntentToMove)

    # Create the chain
    chain = cast(RunnableLambda, prompt | model)

    # Compute score based on hierarchy and open_to_work synthesis results
    scores = [
        state.decision_hierarchy_move.score.value,
        state.decision_openess_to_work.score.value,
    ]
    heuristic_score = (
        "REJECTED"
        if "REJECTED" in scores
        else "REVIEW"
        if "REVIEW" in scores
        else "SUCCESS"
    )

    # Invoke the chain
    res = cast(
        IntentToMove,
        await chain.ainvoke(
            {
                "profile": state.profile.model_dump(mode="json"),
                "synthesis_hierarchy": state.decision_hierarchy_move.model_dump(
                    mode="json"
                ),
                "synthesis_open_to_work": state.decision_openess_to_work.model_dump(
                    mode="json"
                ),
                "system_time": datetime.now().strftime("%B %d, %Y (%Y-%m-%-d)"),
                "output_language": configuration.output_language,
                "score": heuristic_score,
            }
        ),
    )

    return {"decision_intent_to_move": res}
