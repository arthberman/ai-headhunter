from datetime import datetime
from typing import Optional, cast

from langchain_core.runnables import RunnableConfig, RunnableLambda

from analysis.full.state import MainGraphState
from analysis.iterative.configuration import Configuration
from analysis.models.synthesis import LocationSynthesis, SynthesisScore
from analysis.sub_graph.criterion_analysis.models import ScoredCriterion
from scorecard.models.scorecard import CriterionType, ImportanceLevel
from utils import get_prompt, init_model
from utils.candidate_timeline import get_candidate_timeline


def node_synthesis_location(
    state: MainGraphState, config: Optional[RunnableConfig] = None
) -> MainGraphState:
    """Analyze the candidate's location."""
    # Load configuration from the provided RunnableConfig
    configuration = Configuration.from_runnable_config(config)

    # Initialize the prompt
    prompt = get_prompt("candidate-analysis-location")

    # Initialize the model
    raw_model = init_model(configuration.analysis_model)
    model = raw_model.with_structured_output(LocationSynthesis)

    # Create the chain
    chain = cast(RunnableLambda, prompt | model)

    # Get the first scorecard criteria of type location
    criterion = next(
        criterion
        for criterion in state.scorecard.criteria
        if criterion.type == CriterionType.LOCATION
        and criterion.importance_level == ImportanceLevel.MUST_HAVE
    )

    res = cast(
        LocationSynthesis,
        chain.invoke(
            {
                "job_location_criteria": criterion,
                "candidate_timeline": get_candidate_timeline(state.profile),
                "candidate_headline_location": f"{state.profile.city}, {state.profile.state}, {state.profile.country}",
                "output_language": configuration.output_language,
                "system_time": datetime.now().isoformat(),
            }
        ),
    )

    # confidence is 1 if the score is PASS, 0.5 if DOUBT, 0 otherwise
    scored_criterion = ScoredCriterion(
        id=criterion.id,
        score=1
        if res.score == SynthesisScore.PASS
        else 0.5
        if res.score == SynthesisScore.DOUBT
        else 0,
        explanation=res.explanation,
        confidence=1
        if res.score == SynthesisScore.PASS
        else 0.5
        if res.score == SynthesisScore.DOUBT
        else 0,
    )

    return {"synthesis_location": res, "scored_criterion": [scored_criterion]}
