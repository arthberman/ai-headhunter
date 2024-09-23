from typing import List, Optional, cast

from langchain import hub
from langchain.chat_models import init_chat_model
from langchain_core.runnables import Runnable, RunnableConfig
from pydantic import BaseModel, Field

from candidate_matcher.enrichment.experience import Configuration
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
    raw_model = init_model(configuration.enrichment_model)
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


def generate_context(state: ScorecardGraphState) -> ScorecardGraphState:
    """Generate context for the scorecard criteria."""
    model = init_chat_model(
        model="gpt-4o-2024-08-06",
        model_provider="openai",
        temperature=0,
    )

    prompt = hub.pull("generate-scorecard-context")
    structured_model = model.with_structured_output(ListCriterionWithContext)

    scorecard_criteria = [
        {"description": criterion.description}
        for criterion in state.scorecard.mustHaveCriteria
        + state.scorecard.importantCriteria
        + state.scorecard.niceToHaveCriteria
    ]

    chain = cast(Runnable, prompt | structured_model)
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

    new_scorecard = state.scorecard
    # Update output with context for each criterion
    for criterion in (
        new_scorecard.mustHaveCriteria
        + new_scorecard.importantCriteria
        + new_scorecard.niceToHaveCriteria
    ):
        if criterion.description is not None and criterion.description in context_dict:
            criterion.context = context_dict[criterion.description]
        else:
            # No context found for criterion with description
            criterion.context = ""

    return {"scorecard": new_scorecard}


def generate_questions(state: ScorecardGraphState) -> ScorecardGraphState:
    """Generate questions for the scorecard criteria."""
    prompt = hub.pull("generate-scorecard-questions")

    model = init_chat_model(
        model="gpt-4o-2024-08-06", model_provider="openai", temperature=0
    ).with_structured_output(ListQuestions)

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
    state: ScorecardGraphState,
) -> ScorecardGraphState:
    """Generate scoring distribution for the scorecard criteria."""
    prompt = hub.pull("generate-scorecard-scoring-distribution")

    model = init_chat_model(
        model="gpt-4o-2024-08-06", model_provider="openai", temperature=0
    ).with_structured_output(Scorecard)

    chain = cast(Runnable, prompt | model)

    res = cast(
        Scorecard,
        chain.invoke(
            {
                "scorecard": state.scorecard,
            }
        ),
    )

    return {"scorecard": res}


def generate_synthesis(state: ScorecardGraphState) -> ScorecardGraphState:
    """Synthesize the scorecard."""
    model = init_chat_model(
        model="gpt-4o-2024-08-06", model_provider="openai", temperature=0
    )
    structured_model = model.with_structured_output(Synthesis)
    prompt = hub.pull("generate-scorecard-synthesis")

    chain = cast(Runnable, prompt | structured_model)
    synthesis = cast(Synthesis, chain.invoke(state))
    return {"synthesis": synthesis}
