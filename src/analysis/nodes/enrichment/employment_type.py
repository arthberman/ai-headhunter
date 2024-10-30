from datetime import datetime
from typing import Optional, cast

from langchain import hub
from langchain_core.runnables import Runnable, RunnableConfig
from pydantic import BaseModel, Field

from analysis.full.configuration import Configuration
from analysis.full.state import MainGraphState
from utils import format_data, init_model


class StructuredOutput(BaseModel):
    """Structured output for employment type detection."""

    employment_type: str = Field(
        description="The employment type of the experience (Full-time, Part-time, Internship, Apprenticeship, Freelance, Non-Executive Role)"
    )

    explanation: str = Field(
        description="The explanation for the employment type, max 200 characters."
    )

    confidence_score: float = Field(
        description="The confidence score of the employment type (LOW: 0.2 - MEDIUM: 0.5 - HIGH: 0.8)."
    )


def node_find_employment_type(
    state: MainGraphState,
    *,
    config: Optional[RunnableConfig] = None,
) -> MainGraphState:
    """Find employment type of experiences if not provided."""
    # Load configuration from the provided RunnableConfig
    configuration = Configuration.from_runnable_config(config)

    # Initialize the raw model with the provided configuration
    raw_model = init_model(configuration.default_model)

    # Initialize the prompt
    prompt = hub.pull("analysis-find-employment-type:production")

    # Bind the model to the structured output
    model = raw_model.with_structured_output(StructuredOutput)

    # Create the chain
    chain = cast(Runnable, prompt | model)

    # Loop through experiences and update employment types
    updated_experiences = []
    for experience in state.profile.experiences:
        if not experience.employment_type:
            # Invoke the chain for experiences without employment type
            res = cast(
                StructuredOutput,
                chain.invoke(
                    {
                        "experience": format_data(experience),
                        "experiences": format_data(state.profile.experiences),
                        "educations": format_data(state.profile.educations),
                        "system_time": datetime.now().isoformat(),
                    }
                ),
            )

            # Update employment type if confidence score is higher than 70%
            if res.confidence_score >= 0.5:
                experience.employment_type = res.employment_type

        updated_experiences.append(experience)

    # Update the state with the modified experiences
    updated_profile = state.profile.model_copy(
        update={"experiences": updated_experiences}
    )

    return {"profile": updated_profile}
