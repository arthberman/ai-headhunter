from typing import Optional, cast

from langchain import hub
from langchain_core.runnables import RunnableConfig, RunnableLambda

from analysis.iterative.configuration import Configuration
from analysis.iterative.state import MainGraphState
from analysis.models.synthesis import ExtendedScoredCriterion, Synthesis
from analysis.nodes.analysis_subgraph.models import ScoredCriterion
from scorecard.models.scorecard import Scorecard
from utils import format_data, init_model


def extend_scored_criterion(scored_criterion: ScoredCriterion, scorecard: Scorecard):
    """Extend the scored criterion with the scorecard."""
    extended_scored_criterion = []
    for scored_criterion in scored_criterion:
        criterion = next(
            (c for c in scorecard.criteria if c.id == scored_criterion.id),
            None,
        )
        if criterion:
            extended_scored_criterion.append(
                ExtendedScoredCriterion(
                    **scored_criterion.model_dump(),
                    description=criterion.description,
                    importance_level=criterion.importance_level,
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
    prompt = hub.pull("generate-analysis-synthesis")

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
                "profile": format_data(state.profile),
                "extended_scored_criterion": extended_scored_criterion,
                "job_synthesis": state.job_synthesis,
            }
        ),
    )

    return {"synthesis": res}
