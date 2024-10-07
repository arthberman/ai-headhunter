from typing import List, Optional, cast

from langchain import hub
from langchain_core.runnables import Runnable, RunnableConfig
from pydantic import BaseModel, Field

from scorecard_generator.configuration import Configuration
from scorecard_generator.models.job_posting import JobPosting
from scorecard_generator.models.question import ListQuestions
from scorecard_generator.models.scorecard import Scorecard
from scorecard_generator.models.synthesis import Synthesis
from scorecard_generator.state import ScorecardGraphState
from scorecard_generator.utils import init_model


def generate_job_posting(
    state: ScorecardGraphState, *, config: Optional[RunnableConfig] = None
) -> ScorecardGraphState:
    """Generate job posting for the scorecard criteria."""
    # Load configuration from the provided RunnableConfig
    configuration = Configuration.from_runnable_config(config)
    # Initialize the chat model with the provided configuration
    raw_model = init_model(configuration.default_model)
    # Create a structured output model for the JobPosting
    model = raw_model.with_structured_output(JobPosting)
    # Pull the prompt from the hub
    prompt = hub.pull("generate-scorecard-job-posting")
    # Create a chain with the prompt and the model
    chain = cast(Runnable, prompt | model)
    # Invoke the chain with the input data
    output = cast(
        JobPosting,
        chain.invoke(
            {
                "raw_job_posting": state.raw_job_posting,
                "web_context": state.web_context,
            }
        ),
    )

    return {"job_posting": output}


class CriterionWithContext(BaseModel):
    """Criterion with context."""

    criterion_description: str = Field(
        description="Description of the criterion.",
    )
    criterion_context: str = Field(
        description="Context of the criterion. This is the context related to the criterion.",
    )


class ListCriterionWithContext(BaseModel):
    """List of criteria with context."""

    criteria: List[CriterionWithContext] = Field(
        description="List of criteria with context.",
    )


def generate_context(
    state: ScorecardGraphState, *, config: Optional[RunnableConfig] = None
) -> ScorecardGraphState:
    """Generate context for the scorecard criteria."""
    # Load configuration from the provided RunnableConfig
    configuration = Configuration.from_runnable_config(config)

    # Initialize the raw model with the provided configuration
    raw_model = init_model(configuration.default_model)

    # Create a structured output model for the ListCriterionWithContext
    model = raw_model.with_structured_output(ListCriterionWithContext)

    prompt = hub.pull("generate-scorecard-context")

    scorecard_criteria = [
        {"description": criterion.description}
        for criterion in state.scorecard.must_have_criteria
        + state.scorecard.important_criteria
        + state.scorecard.nice_to_have_criteria
    ]

    chain = cast(Runnable, prompt | model)
    output = cast(
        ListCriterionWithContext,
        chain.invoke(
            {
                "raw_job_posting": state.raw_job_posting,
                "web_context": state.web_context,
                "human_context": state.human_context,
                "scorecard_criteria": scorecard_criteria,
            }
        ),
    )

    # Create a dictionary for easier lookup
    context_dict = {
        c.criterion_description: c.criterion_context for c in output.criteria
    }

    new_scorecard = state.scorecard.model_copy()
    # Update output with context for each criterion
    for criterion in (
        new_scorecard.must_have_criteria
        + new_scorecard.important_criteria
        + new_scorecard.nice_to_have_criteria
    ):
        if criterion.description is not None and criterion.description in context_dict:
            criterion.context = context_dict[criterion.description]
        else:
            # No context found for criterion with description
            criterion.context = ""

    return {"scorecard": new_scorecard}


def generate_questions(
    state: ScorecardGraphState, *, config: Optional[RunnableConfig] = None
) -> ScorecardGraphState:
    """Generate questions for the scorecard criteria."""
    # Load configuration from the provided RunnableConfig
    configuration = Configuration.from_runnable_config(config)

    prompt = hub.pull("generate-scorecard-questions")

    model = init_model(configuration.default_model).with_structured_output(
        ListQuestions
    )

    chain = cast(Runnable, prompt | model)

    res = cast(
        ListQuestions,
        chain.invoke(
            {
                "raw_job_posting": state.raw_job_posting,
                "web_context": state.web_context,
            }
        ),
    )

    return {"generated_questions": res.questions}


def generate_scoring_distribution(
    state: ScorecardGraphState, *, config: Optional[RunnableConfig] = None
) -> ScorecardGraphState:
    """Generate scoring distribution for the scorecard criteria."""
    prompt = hub.pull("generate-scorecard-scoring-distribution")

    configuration = Configuration.from_runnable_config(config)

    model = init_model(configuration.default_model).with_structured_output(Scorecard)

    chain = cast(Runnable, prompt | model)

    res = cast(
        Scorecard,
        chain.invoke(
            {
                "scorecard": state.scorecard,
            }
        ),
    )

    return {
        "scorecard": res,
        "human_feedback": state.human_feedback,
        "human_context": state.human_context,
    }


def generate_synthesis(
    state: ScorecardGraphState, *, config: Optional[RunnableConfig] = None
) -> ScorecardGraphState:
    """Synthesize the scorecard."""
    configuration = Configuration.from_runnable_config(config)

    raw_model = init_model(configuration.default_model)

    model = raw_model.with_structured_output(Synthesis)
    prompt = hub.pull("generate-scorecard-synthesis")

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
