from datetime import datetime
from statistics import mean, median
from typing import Optional, cast

from langchain import hub
from langchain_core.runnables import RunnableConfig, RunnableLambda

from analysis.full.state import MainGraphState
from analysis.iterative.configuration import Configuration
from analysis.models.synthesis import MustSynthesis, SynthesisScore
from scorecard.models.scorecard import ImportanceLevel
from utils import get_extended_scored_criterion, init_model


def node_synthesis_must(
    state: MainGraphState, config: Optional[RunnableConfig] = None
) -> MainGraphState:
    """Synthesize the must criteria."""
    # Load configuration from the provided RunnableConfig
    configuration = Configuration.from_runnable_config(config)

    # Get scored criteria for Must
    scored_must_criteria = get_extended_scored_criterion(
        state.scored_criterion,
        state.scorecard,
        importance_level=ImportanceLevel.MUST_HAVE,
    )

    # Calculate scores
    heuristic_result = MustSynthesis(score=SynthesisScore.FAIL, explanation="")
    scores = [criterion.score for criterion in scored_must_criteria]
    confidence_scores = [criterion.confidence for criterion in scored_must_criteria]
    min_score = min(scores) if scores else 0
    mean_score = mean(scores) if scores else 0
    median_score = median(scores) if scores else 0
    score_spread = abs(
        mean_score - median_score
    )  # Difference between mean and median indicates outliers
    avg_confidence = sum(confidence_scores) / len(confidence_scores)

    if min_score >= 0.6:
        heuristic_result.score = SynthesisScore.PASS
        heuristic_result.explanation = "All criteria meet minimum threshold"
    elif min_score <= 0.3:
        heuristic_result.score = SynthesisScore.FAIL
        heuristic_result.explanation = "At least one criterion severely underperforms"
    elif score_spread > 0.2:  # High difference between mean and median
        heuristic_result.score = SynthesisScore.DOUBT
        heuristic_result.explanation = "Inconsistent performance across criteria"
    elif (
        median_score > 0.5
    ):  # Use median for better representation of typical performance
        heuristic_result.score = SynthesisScore.DOUBT
        heuristic_result.explanation = "Typical performance is borderline"
    else:
        heuristic_result.score = SynthesisScore.FAIL
        heuristic_result.explanation = "Overall performance below requirements"

    if avg_confidence < 0.6 and heuristic_result.score == SynthesisScore.PASS:
        heuristic_result.score = SynthesisScore.DOUBT
        heuristic_result.explanation += " (Low confidence in assessment)"

    # Initialize the prompt
    prompt = hub.pull("analysis-synthesis-must")

    # Initialize the model
    raw_model = init_model(configuration.analysis_model)
    model = raw_model.with_structured_output(MustSynthesis)

    # Create the chain
    chain = cast(RunnableLambda, prompt | model)

    ai_result = cast(
        MustSynthesis,
        chain.invoke(
            {
                "scored_must_criteria": scored_must_criteria,
                "heuristic_result": heuristic_result.model_dump(),
                "output_language": "en",
                "system_time": datetime.now().isoformat(),
            },
        ),
    )

    return {"synthesis_must": ai_result}
