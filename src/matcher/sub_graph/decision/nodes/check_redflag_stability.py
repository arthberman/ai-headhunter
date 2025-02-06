from datetime import datetime
from typing import cast

from langchain_core.runnables import Runnable, RunnableConfig

from matcher.configuration import Configuration
from matcher.state import MainGraphState
from matcher.sub_graph.decision.models import RedflagStability
from utils import (
    FewShotConfig,
    get_candidate_timeline,
    get_few_shot_messages,
    get_prompt,
    init_model,
)


async def node_check_decision_redflag_stability(
    state: MainGraphState, config: RunnableConfig
):
    """Analyze the candidate's redflag stability."""
    # Load configuration from the provided RunnableConfig
    configuration = Configuration.from_runnable_config(config)

    # Initialize the raw model with the provided configuration
    raw_model = init_model(configuration.matcher_model)

    # Initialize the prompt
    prompt = get_prompt("check-redflag-stability")

    # Few shot
    few_shot_config = FewShotConfig(
        dataset_name="fs-check-redflag-stability",
        input_keys=["profile_details"],
        output_keys=["score", "explanation"],
        input_template="Profile details: {profile_details}",
        output_template="""Score: {score}\nExplanation: {explanation}""",
    )

    few_shot_messages = await get_few_shot_messages(few_shot_config)

    # Bind the model to the structured output
    model = raw_model.with_structured_output(RedflagStability)

    # Create the chain
    chain = cast(Runnable, prompt | model)

    # Invoke the chain
    res = cast(
        RedflagStability,
        await chain.ainvoke(
            {
                "candidate_timeline": get_candidate_timeline(
                    state.profile, with_detail=True
                ).model_dump(mode="json"),
                "examples": few_shot_messages,
                "output_language": configuration.output_language,
                "system_time": datetime.now().strftime("%B %d, %Y (%Y-%m-%-d)"),
            }
        ),
    )

    return {"decision_redflag_stability": res}
