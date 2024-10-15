from typing import List, Optional, cast

from langchain import hub
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable, RunnableConfig
from pydantic import BaseModel, Field
from trustcall import create_extractor

from scorecard.configuration import Configuration
from scorecard.state import ScorecardGraphState
from utils import init_model
from scorecard.models.job_posting import JobPosting
from scorecard.models.question import ListQuestions
from scorecard.models.scorecard import Scorecard, ScoringDistribution
from scorecard.models.synthesis import Synthesis


class CriterionScoringDistribution(BaseModel):
    """Criterion ID and its scoring distribution."""

    criterion_id: str = Field(description="ID of the criterion.")
    scoring_distribution: ScoringDistribution = Field(
        description="Scoring distribution for the criterion."
    )


class ListCriterionScoringDistributions(BaseModel):
    """List of criterion scoring distributions."""

    distributions: List[CriterionScoringDistribution] = Field(
        description="List of criterion scoring distributions."
    )


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

    criterion_id: str = Field(
        description="ID of the criterion.",
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
    """Generate context for the scorecard criteria without existing context."""
    # Load configuration from the provided RunnableConfig
    configuration = Configuration.from_runnable_config(config)

    # Initialize the raw model with the provided configuration
    raw_model = init_model(configuration.default_model)

    # Create a structured output model for the ListCriterionWithContext
    model = raw_model.with_structured_output(ListCriterionWithContext)

    prompt = hub.pull("generate-scorecard-context")

    # Filter criteria without context
    criteria_without_context = [
        {"id": criterion.id, "description": criterion.description}
        for criterion in state.scorecard.criteria
        if not criterion.context
    ]

    # If all criteria have context, return the current state
    if not criteria_without_context:
        return {"scorecard": state.scorecard}

    chain = cast(Runnable, prompt | model)
    output = cast(
        ListCriterionWithContext,
        chain.invoke(
            {
                "raw_job_posting": state.raw_job_posting,
                "web_context": state.web_context,
                "human_context": state.human_context,
                "scorecard_criteria": criteria_without_context,
            }
        ),
    )

    # Create a dictionary for easier lookup, using empty string as default
    context_dict = {
        c.criterion_id: c.criterion_context or "No context provided"
        for c in output.criteria
    }

    new_scorecard = state.scorecard.model_copy()
    # Update output with context for each criterion without existing context
    for criterion in new_scorecard.criteria:
        if not criterion.context:
            criterion.context = context_dict.get(criterion.id, "No context provided")

    return {"scorecard": new_scorecard}


def generate_questions(
    state: ScorecardGraphState, *, config: Optional[RunnableConfig] = None
) -> ScorecardGraphState:
    """Generate questions for the scorecard criteria."""
    # Load configuration from the provided RunnableConfig
    configuration = Configuration.from_runnable_config(config)

    prompt = hub.pull("generate-scorecard-questions")
    chat_prompt = ChatPromptTemplate.from_messages(prompt.messages)

    formatted_messages = chat_prompt.format_messages(
        raw_job_posting=state.raw_job_posting,
        web_context=state.web_context,
    )

    raw_model = init_model(configuration.structure_model)

    extractor = create_extractor(raw_model, tools=[ListQuestions])

    res = cast(
        ListQuestions,
        extractor.invoke(
            {
                "messages": formatted_messages,
                # "existing": {"ListQuestions": existing_questions.model_dump()},
            }
        )["responses"][0],
    )

    return {"generated_questions": res}


def generate_scoring_distribution(
    state: ScorecardGraphState, *, config: Optional[RunnableConfig] = None
) -> ScorecardGraphState:
    """Generate scoring distribution for the scorecard criteria without existing distributions."""
    prompt = hub.pull("generate-scorecard-scoring-distribution")

    configuration = Configuration.from_runnable_config(config)

    model = init_model(configuration.default_model).with_structured_output(
        ListCriterionScoringDistributions
    )

    # Filter criteria without scoring distribution
    criteria_without_distribution = [
        criterion.model_dump()
        for criterion in state.scorecard.criteria
        if not criterion.scoring_distribution
    ]

    # If all criteria have scoring distributions, return the current state
    if not criteria_without_distribution:
        return {
            "scorecard": state.scorecard,
            "human_feedback": state.human_feedback,
            "human_context": state.human_context,
        }

    chain = cast(Runnable, prompt | model)

    res = cast(
        ListCriterionScoringDistributions,
        chain.invoke(
            {
                "scorecard_criteria": criteria_without_distribution,
            }
        ),
    )

    # Create a dictionary for easier lookup
    distribution_dict = {
        d.criterion_id: d.scoring_distribution for d in res.distributions
    }

    # Update the scorecard with the new scoring distributions
    new_scorecard = state.scorecard.model_copy()
    for criterion in new_scorecard.criteria:
        if not criterion.scoring_distribution and criterion.id in distribution_dict:
            criterion.scoring_distribution = distribution_dict[criterion.id]

    return {
        "scorecard": new_scorecard,
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


def generate_scorecard_structure(
    state: ScorecardGraphState, *, config: Optional[RunnableConfig] = None
) -> ScorecardGraphState:
    """Generate a scorecard structure based on the given state."""
    # Load configuration from the provided RunnableConfig
    configuration = Configuration.from_runnable_config(config)
    # Initialize the chat model with the provided configuration
    raw_model = init_model(configuration.structure_model)

    extractor = create_extractor(raw_model, tools=[Scorecard])

    hub_prompt = hub.pull("generate-scorecard-structure")
    chat_prompt = ChatPromptTemplate.from_messages(hub_prompt.messages)

    formatted_messages = chat_prompt.format_messages(
        raw_job_posting=state.raw_job_posting,
        web_context=state.web_context,
        generated_questions=state.generated_questions,
    )

    res = cast(Scorecard, extractor.invoke(formatted_messages)["responses"][0])

    return {"scorecard": res}


def judge_scorecard_structure(
    state: ScorecardGraphState, *, config: Optional[RunnableConfig] = None
) -> ScorecardGraphState:
    """Generate a scorecard structure based on the given state."""
    # Load configuration from the provided RunnableConfig
    configuration = Configuration.from_runnable_config(config)
    # Initialize the chat model with the provided configuration
    raw_model = init_model(configuration.structure_model)

    extractor = create_extractor(raw_model, tools=[Scorecard])

    prompt = hub.pull("judge-scorecard-structure")
    chat_prompt = ChatPromptTemplate.from_messages(prompt.messages)

    formatted_messages = chat_prompt.format_messages()

    res = cast(
        Scorecard,
        extractor.invoke(
            {
                "messages": formatted_messages,
                "existing": {"Scorecard": state.scorecard.model_dump()},
            }
        )["responses"][0],
    )

    return {"scorecard": res}
