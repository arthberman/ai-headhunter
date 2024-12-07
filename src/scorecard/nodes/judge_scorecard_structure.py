from typing import cast

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableConfig
from trustcall import create_extractor

from scorecard.configuration import Configuration
from scorecard.models.scorecard import BaseCriterion, Scorecard
from scorecard.nodes.scorecard_structure import LimitedScorecard
from scorecard.state import ScorecardGraphState
from utils import get_prompt, init_model


def node_judge_scorecard_structure(
    state: ScorecardGraphState, *, config: RunnableConfig
) -> ScorecardGraphState:
    """Judge and potentially modify the scorecard structure."""
    configuration = Configuration.from_runnable_config(config)
    raw_model = init_model(configuration.structure_model)
    extractor = create_extractor(
        raw_model, tools=[LimitedScorecard], tool_choice="LimitedScorecard"
    )

    limited_scorecard = LimitedScorecard(**state.scorecard.model_dump())

    prompt = get_prompt("judge-scorecard-structure")
    chat_prompt = ChatPromptTemplate.from_messages(prompt.messages)

    formatted_messages = chat_prompt.format_messages()

    res = cast(
        LimitedScorecard,
        extractor.invoke(
            {
                "messages": formatted_messages,
                "existing": {
                    "LimitedScorecard": limited_scorecard.model_dump(mode="json")
                },
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
                category=criterion.category,
                priority=criterion.priority,
                context=existing_criteria.get(criterion.description, (None, None))[0],
                scoring_distribution=existing_criteria.get(
                    criterion.description, (None, None)
                )[1],
            )
            for criterion in res.criteria
        ],
    )

    return {"scorecard": scorecard_new}
