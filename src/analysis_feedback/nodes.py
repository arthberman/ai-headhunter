from typing import Optional, cast

from langchain import hub
from langchain_core.runnables import Runnable, RunnableConfig

from analysis_feedback.configuration import Configuration
from analysis_feedback.models import (
    ProfileRelatedElement,
    ReformedHumanFeedback,
    ScorecardRelatedElement,
    SynthesizedFeedback,
)
from analysis_feedback.state import MainGraphState
from analysis_feedback.utils import init_model, log_cancelled_error


@log_cancelled_error
def node_reformulate_human_feedback(
    state: MainGraphState, *, config: Optional[RunnableConfig] = None
) -> MainGraphState:
    """Reformulate the human feedback."""
    # Load configuration from the provided RunnableConfig
    configuration = Configuration.from_runnable_config(config)

    # Initialize the raw model with the provided configuration
    raw_model = init_model(configuration.reformulation_model)

    # Create a structured output model for the JobPosting
    model = raw_model.with_structured_output(ReformedHumanFeedback)

    # Pull the prompt from the hub
    prompt = hub.pull("analysis-feedback-reformulate")

    # Create a chain with the prompt and the model
    chain = cast(Runnable, prompt | model)

    # Invoke the chain with the input data
    output = cast(
        ReformedHumanFeedback,
        chain.invoke({"human_feedback": state.raw_human_feedback}),
    )

    return {"human_feedback": output.reformed_human_feedback}


@log_cancelled_error
def node_extract_profile_related_elements(
    state: MainGraphState, *, config: Optional[RunnableConfig] = None
) -> MainGraphState:
    """Extract the profile related elements."""
    # Load configuration from the provided RunnableConfig
    configuration = Configuration.from_runnable_config(config)

    # Initialize the raw model with the provided configuration
    raw_model = init_model(configuration.reformulation_model)

    # Create a structured output model for the JobPosting
    model = raw_model.with_structured_output(ProfileRelatedElement)

    # Pull the prompt from the hub
    prompt = hub.pull("analysis-feedback-extract-profile")

    # Create a chain with the prompt and the model
    chain = cast(Runnable, prompt | model)

    # Invoke the chain with the input data
    output = cast(
        ProfileRelatedElement,
        chain.invoke(
            {
                "human_feedback": state.human_feedback,
                "candidate_profile": state.candidate_profile.model_dump()
                if state.candidate_profile
                else None,
            }
        ),
    )

    return {"profile_related_elements": output}


@log_cancelled_error
def node_extract_scorecard_related_elements(
    state: MainGraphState, *, config: Optional[RunnableConfig] = None
) -> MainGraphState:
    """Extract the scorecard related elements."""
    # Load configuration from the provided RunnableConfig
    configuration = Configuration.from_runnable_config(config)

    # Initialize the raw model with the provided configuration
    raw_model = init_model(configuration.reformulation_model)

    # Create a structured output model for the JobPosting
    model = raw_model.with_structured_output(ScorecardRelatedElement)

    # Pull the prompt from the hub
    prompt = hub.pull("analysis-feedback-extract-scorecard")

    # Create a chain with the prompt and the model
    chain = cast(Runnable, prompt | model)

    # Invoke the chain with the input data
    output = cast(
        ScorecardRelatedElement,
        chain.invoke(
            {
                "human_feedback": state.human_feedback,
                "scored_criteria": state.scored_criteria.model_dump()
                if state.scored_criteria
                else [],
            }
        ),
    )

    return {"scorecard_related_elements": output}


def node_synthesize_feedback(
    state: MainGraphState, *, config: Optional[RunnableConfig] = None
) -> MainGraphState:
    """Iterate the scorecard."""
    # Load configuration from the provided RunnableConfig
    configuration = Configuration.from_runnable_config(config)

    # Initialize the raw model with the provided configuration
    raw_model = init_model(configuration.reformulation_model)

    # Create a structured output model for the JobPosting
    model = raw_model.with_structured_output(SynthesizedFeedback)

    # Pull the prompt from the hub
    prompt = hub.pull("analysis-feedback-synthesize")

    # Create a chain with the prompt and the model
    chain = cast(Runnable, prompt | model)

    # Invoke the chain with the input data
    output = cast(
        SynthesizedFeedback,
        chain.invoke(
            {
                "human_feedback": state.human_feedback,
                "scorecard_related_elements": state.scorecard_related_elements.model_dump()
                if state.scorecard_related_elements
                else None,
                "profile_related_elements": state.profile_related_elements.model_dump()
                if state.profile_related_elements
                else None,
            }
        ),
    )

    return {
        "synthesized_feedback": output.synthesized_feedback,
        "is_actionable_and_relevant": output.is_actionable_and_relevant,
    }
