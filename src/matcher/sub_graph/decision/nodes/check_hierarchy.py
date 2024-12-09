from datetime import datetime
from typing import cast

from langchain_core.runnables import Runnable, RunnableConfig

from matcher.configuration import Configuration
from matcher.state import MainGraphState
from matcher.sub_graph.decision.models import HierarchyMove
from utils import get_candidate_timeline, get_prompt, init_model


async def node_check_hierarchy(state: MainGraphState, config: RunnableConfig):
    """Analyze the language proficiency of the candidate."""
    # Load configuration from the provided RunnableConfig
    configuration = Configuration.from_runnable_config(config)

    # Initialize the raw model with the provided configuration
    raw_model = init_model(configuration.matcher_model)

    # Initialize the prompt
    prompt = get_prompt("candidate-analysis-hierarchy")

    # Bind the model to the structured output
    model = raw_model.with_structured_output(HierarchyMove)

    # Create the chain
    chain = cast(Runnable, prompt | model)

    # Invoke the chain
    res = cast(
        HierarchyMove,
        await chain.ainvoke(
            {
                "candidate_timeline": get_candidate_timeline(
                    state.profile, with_detail=True
                ).model_dump(mode="json"),
                "target_role": state.job_synthesis,
                "output_language": configuration.output_language,
                "system_time": datetime.now().strftime("%B %d, %Y (%Y-%m-%-d)"),
            }
        ),
    )

    return {"hierarchy_move": res}
