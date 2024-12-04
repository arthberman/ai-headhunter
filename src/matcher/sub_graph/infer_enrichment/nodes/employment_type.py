from datetime import datetime
from typing import cast

from langchain_core.runnables import Runnable, RunnableConfig
from pydantic import BaseModel, Field

from matcher.configuration import Configuration
from matcher.sub_graph.infer_enrichment.state import MainInferEnrichmentState
from utils import (
    FewShotConfig,
    format_data,
    get_few_shot_messages,
    get_prompt,
    init_model,
)
from utils.candidate_timeline import get_candidate_timeline


class EmploymentType(BaseModel):
    """Employment type detection."""

    id: int = Field(..., description="ID of the experience.")

    type: str = Field(
        ...,
        description="Employment type of the experience (Full-time, Part-time, Internship, Apprenticeship, Freelance, Non-Executive Role)",
    )

    explanation: str = Field(
        ..., description="Explanation for the employment type, max 200 characters."
    )

    confidence: float = Field(
        ...,
        description="Confidence score of the employment type (LOW: 0.2 - MEDIUM: 0.5 - HIGH: 0.8).",
    )


class ListEmploymentType(BaseModel):
    """List of employment types."""

    employments: list[EmploymentType] = Field(
        ..., description="List of employment types."
    )


def node_infer_employment_type(
    state: MainInferEnrichmentState,
    *,
    config: RunnableConfig,
) -> MainInferEnrichmentState:
    """Find employment type of experiences if not provided."""
    # Load configuration from the provided RunnableConfig
    configuration = Configuration.from_runnable_config(config)

    # Initialize the raw model with the provided configuration
    raw_model = init_model(configuration.default_model)

    # Initialize the prompt
    prompt = get_prompt("analysis-find-employment-type")

    # Bind the model to the structured output
    model = raw_model.with_structured_output(ListEmploymentType)

    # Create the chain
    chain = cast(Runnable, prompt | model)

    # Few shot
    few_shot_config = FewShotConfig(
        dataset_name="fs-find-employment-type",
        input_keys=["experience"],
        output_keys=["employment_type", "confidence", "explanation"],
        input_template="Experience: {experience}",
        output_template="""
                Employment type: {employment_type}
                Confidence: {confidence}
                Explanation: {explanation}
                """,
    )

    few_shot_messages = get_few_shot_messages(few_shot_config)

    # Loop through experiences and update employment types
    updated_experiences = []

    # Experiences without employment type
    experiences_without_employment_type = [
        (i, experience)
        for i, experience in enumerate(state.profile.experiences)
        if not experience.employment_type
    ]

    if not experiences_without_employment_type:
        return {"profile": state.profile}

    # Format experiences with their IDs for the LLM
    formatted_experiences = [
        {"id": idx, "experience": format_data(exp)}
        for idx, exp in experiences_without_employment_type
    ]

    res = cast(
        ListEmploymentType,
        chain.invoke(
            {
                "experiences": format_data(formatted_experiences),
                "candidate_timeline": format_data(
                    get_candidate_timeline(state.profile)
                ),
                "examples": few_shot_messages,
                "output_language": configuration.output_language,
                "system_time": datetime.now().strftime("%d %B %Y (%d-%m-%Y)"),
            }
        ),
    )

    for employment_type in res.employments:
        if employment_type.confidence >= 0.5:
            # find experience by ID
            experience = next(
                (
                    exp
                    for idx, exp in experiences_without_employment_type
                    if idx == employment_type.id
                ),
                None,
            )
            if experience is None:
                raise ValueError(f"Experience with ID {employment_type.id} not found")

            # Create a copy of the experience with the updated employment type
            updated_exp = experience.model_copy(
                update={"employment_type": employment_type.type}
            )
            updated_experiences.append(updated_exp)

    # Update the state with the modified experiences
    updated_profile = state.profile.model_copy(
        update={"experiences": updated_experiences}
    )
    return {"profile": updated_profile}
