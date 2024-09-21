from typing import Optional, cast

from langchain import hub
from langchain.chat_models import init_chat_model
from langchain_core.runnables import RunnableConfig, RunnableLambda

from candidate_matcher.analysis.models import ScoredCriterion
from candidate_matcher.state import MainGraphState
from candidate_matcher.synthesis.models import ExtendedScoredCriterion, Synthesis
from src.candidate_matcher.configuration import Configuration
from src.candidate_matcher.utils import init_model
from src.scorecard_generator.models.scorecard import ImportanceLevel, Scorecard


def extend_scored_criterion(scored_criterion: ScoredCriterion, scorecard: Scorecard):
    """Extend the scored criterion with the scorecard."""

    extended_scored_criterion = []
    for scored_criterion in scored_criterion:
        criterion = next(
            (
                c
                for c in scorecard.mustHaveCriteria
                + scorecard.importantCriteria
                + scorecard.niceToHaveCriteria
                if c.id == scored_criterion.id
            ),
            None,
        )
        if criterion:
            extended_scored_criterion.append(
                ExtendedScoredCriterion(
                    **scored_criterion.model_dump(),
                    description=criterion.description,
                    importance_level=(
                        ImportanceLevel.MUST_HAVE
                        if criterion in scorecard.mustHaveCriteria
                        else (
                            ImportanceLevel.IMPORTANT
                            if criterion in scorecard.importantCriteria
                            else ImportanceLevel.NICE_TO_HAVE
                        )
                    ),
                    criterion_type=criterion.type,
                )
            )

    return extended_scored_criterion


def node_synthesis(
    state: MainGraphState, config: Optional[RunnableConfig] = None
) -> MainGraphState:
    """Synthesize the output."""

    # Load configuration from the provided RunnableConfig
    configuration = Configuration.from_runnable_config(config)

    # Initialize the prompt
    prompt = hub.pull("analyse-synthesis")

    # Initialize the model
    raw_model = init_model(configuration.synthesis_model)
    model = raw_model.with_structured_output(Synthesis)

    # Create the chain
    chain = cast(RunnableLambda, prompt | model)

    # Extend the scored criterion with the scorecard
    extended_scored_criterion = extend_scored_criterion(
        state.scored_criterion, state.scorecard
    )

    # Invoke the chain
    res = cast(
        Synthesis,
        chain.invoke(
            {
                "profile": state.profile,
                "extended_scored_criterion": extended_scored_criterion,
                "scorecard_synthesis": state.scorecard_synthesis,
            }
        ),
    )

    return {"synthesis": res}
