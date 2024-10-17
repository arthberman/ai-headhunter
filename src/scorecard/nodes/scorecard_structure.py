from typing import List, Optional, cast

from langchain import hub
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableConfig
from pydantic import Field
from pydantic.json_schema import SkipJsonSchema
from trustcall import create_extractor

from scorecard.configuration import Configuration
from scorecard.models.scorecard import BaseCriterion, Scorecard, ScoringDistribution
from scorecard.state import ScorecardGraphState
from utils import init_model


class LimitedBaseCriterion(BaseCriterion):
    """Base criterion without context and scoring distribution."""

    context: SkipJsonSchema[Optional[str]] = Field(
        None,
        description="This is the context of the job posting that is relevant to the criterion (definition of the scope).",
        exclude=True,
    )
    scoring_distribution: SkipJsonSchema[Optional[ScoringDistribution]] = Field(
        None,
        description="The type of scoring distribution for this criterion",
        exclude=True,
    )


class LimitedScorecard(Scorecard):
    """Scorecard with limited context and scoring distribution."""

    criteria: List[LimitedBaseCriterion] = Field(
        default_factory=list, description="List of criteria in the scorecard"
    )


prompt_iterative_instruction = """
You are in the UPDATE stage of the scorecard design process.
You are given a job scorecard to update based on the human feedback.
Do not suggest changes that aren't directly addressed in the human feedback.

When updating the scorecard, you must only follow the human feedback provided :
<human_feedback>
{human_feedback}
</human_feedback>
"""


def node_scorecard_structure(
    state: ScorecardGraphState, *, config: Optional[RunnableConfig] = None
) -> ScorecardGraphState:
    """Generate a scorecard structure based on the human feedback."""
    # Load configuration from the provided RunnableConfig
    configuration = Configuration.from_runnable_config(config)
    # Initialize the chat model with the provided configuration
    raw_model = init_model(configuration.structure_model)

    if state.scorecard:
        limited_scorecard = LimitedScorecard(**state.scorecard.model_dump())

    extractor = create_extractor(raw_model, tools=[LimitedScorecard])

    hub_prompt = hub.pull("generate-scorecard-structure")
    chat_prompt = ChatPromptTemplate.from_messages(hub_prompt.messages)

    formatted_messages = chat_prompt.format_messages(
        raw_job_posting=state.raw_job_posting,
        web_context=state.web_context,
        human_context=state.human_context,
        iterative_instruction=(
            prompt_iterative_instruction.format(human_feedback=state.human_feedback)
            if state.scorecard and state.human_feedback
            else ""
        ),
    )

    res = cast(
        LimitedScorecard,
        extractor.invoke(
            {
                "messages": formatted_messages,
                "existing": (
                    {"LimitedScorecard": limited_scorecard.model_dump()}
                    if state.scorecard and limited_scorecard
                    else None
                ),
            }
        )["responses"][0],
    )

    # Create a dictionary to map descriptions to context and scoring_distribution
    existing_criteria = {}
    if state.scorecard:
        existing_criteria = {
            criterion.description: (criterion.context, criterion.scoring_distribution)
            for criterion in state.scorecard.criteria
        }

    # Create scorecard_new from res and with the context and scoring distribution by copying from the original scorecard
    scorecard_new = Scorecard(
        criteria=[
            BaseCriterion(
                description=criterion.description,
                type=criterion.type,
                importance_level=criterion.importance_level,
                context=existing_criteria.get(criterion.description, (None, None))[0],
                scoring_distribution=existing_criteria.get(
                    criterion.description, (None, None)
                )[1],
            )
            for criterion in res.criteria
        ],
    )

    print(scorecard_new)

    return {
        "scorecard": scorecard_new,
        "human_context": (state.human_context or []) + (state.human_feedback or []),
        "human_feedback": [],
    }
