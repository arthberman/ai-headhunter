from datetime import datetime
from typing import cast

from langchain_core.runnables import Runnable, RunnableConfig
from pydantic import BaseModel, Field

from matcher.configuration import Configuration
from matcher.state import MainGraphState
from utils import get_prompt, init_model
from utils.few_shot import FewShotConfig, get_few_shot_messages


class RoleTrajectory(BaseModel):
    """Analysis of a candidate role trajectory over time."""

    explanation: str = Field(
        ...,
        description="Comprehensive narrative explaining the candidate role progression, including significant transitions, specializations, and overall professional direction (max 600 characters)",
    )


async def node_infer_role_trajectory(
    state: MainGraphState,
    *,
    config: RunnableConfig,
):
    """Estimate the role trajectory of the profile."""
    # Load configuration from the provided RunnableConfig
    configuration = Configuration.from_runnable_config(config)

    # Initialize the raw model with the provided configuration
    raw_model = init_model(configuration.default_model)

    # Initialize the prompt
    prompt = get_prompt("candidate-analysis-role-trajectory")

    # Few shot
    few_shot_config = FewShotConfig(
        dataset_name="fs-candidate-analysis-role-trajectory",
        input_keys=["profile_detail"],
        output_keys=["explanation"],
        input_template="Profile details: {profile_detail}",
        output_template="""Explanation: {explanation}""",
    )

    few_shot_messages = await get_few_shot_messages(few_shot_config)

    # Bind the model to the structured output
    model = raw_model.with_structured_output(RoleTrajectory)

    # Create the chain
    chain = cast(Runnable, prompt | model)

    res = cast(
        RoleTrajectory,
        await chain.ainvoke(
            {
                "profile": state.profile.model_dump(mode="json"),
                "examples": few_shot_messages,
                "system_time": datetime.now().strftime("%B %d, %Y (%Y-%m-%-d)"),
            }
        ),
    )

    return {"inferred_role_trajectory": res.explanation}
