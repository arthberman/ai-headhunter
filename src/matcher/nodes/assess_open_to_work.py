from datetime import datetime
from typing import cast

from langchain_core.runnables import Runnable, RunnableConfig

from matcher.configuration import Configuration
from matcher.models.synthesis import OpenToWorkSynthesis, SynthesisScore
from matcher.state import MainGraphState
from utils import (
    FewShotConfig,
    get_candidate_timeline,
    get_few_shot_messages,
    get_prompt,
    init_model,
)


async def node_assess_open_to_work(state: MainGraphState, config: RunnableConfig):
    """Analyze the candidate's openess to work, awareness of new opportunities."""
    # Load configuration from the provided RunnableConfig
    configuration = Configuration.from_runnable_config(config)

    # Already open to work on his profile
    if state.profile.is_open_to_work:
        return {
            "synthesis_open_to_work": OpenToWorkSynthesis(
                score=SynthesisScore.PASS,
                explanation="This candidate is declared as Open To Work on his profile.",
            )
        }

    # Initialize the raw model with the provided configuration
    raw_model = init_model(configuration.matcher_model)

    # Initialize the prompt
    prompt = get_prompt("candidate-analysis-open-to-work")

    # Few shot
    few_shot_config = FewShotConfig(
        dataset_name="fs-candidate-analysis-open-to-work",
        input_keys=["profile_details"],
        output_keys=["score", "explanation"],
        input_template="Profile details: {profile_details}",
        output_template="""Score: {score}\nExplanation: {explanation}""",
    )

    few_shot_messages = await get_few_shot_messages(few_shot_config)

    # Bind the model to the structured output
    model = raw_model.with_structured_output(OpenToWorkSynthesis)

    # Create the chain
    chain = cast(Runnable, prompt | model)

    # Invoke the chain
    res = cast(
        OpenToWorkSynthesis,
        await chain.ainvoke(
            {
                "candidate_timeline": get_candidate_timeline(
                    state.profile, with_detail=True
                ).model_dump(mode="json"),
                "examples": few_shot_messages,
                "target_role": state.job_synthesis,
                "output_language": configuration.output_language,
                "system_time": datetime.now().strftime("%d %B %Y (%d-%m-%Y)"),
            }
        ),
    )

    return {"synthesis_open_to_work": res}
