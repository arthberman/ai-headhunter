from statistics import mean, median
from typing import List

from matcher.models.synthesis import MustSynthesis, SynthesisScore
from matcher.sub_graph.criterion_matcher.models import ScoredCriterion
from setup.models.scorecard import Priority, Scorecard
from utils.get_extended_scored_criterion import get_extended_scored_criterion


def compute_must_score(
    scored_criterion: List[ScoredCriterion], scorecard: Scorecard
) -> MustSynthesis:
    """Compute the must score heuristically."""
    # Get scored criteria for Must
    scored_must_criteria = get_extended_scored_criterion(
        scored_criterion,
        scorecard,
        priority=Priority.REQUIRED,
    )

    # Calculate scores
    heuristic_result = MustSynthesis(score=SynthesisScore.REJECTED, explanation="")
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
        heuristic_result.score = SynthesisScore.ACCEPTED
        heuristic_result.explanation = "All criteria meet minimum threshold"
    elif min_score <= 0.3:
        heuristic_result.score = SynthesisScore.REJECTED
        heuristic_result.explanation = "At least one criterion severely underperforms"
    elif score_spread > 0.2:  # High difference between mean and median
        heuristic_result.score = SynthesisScore.REVIEW
        heuristic_result.explanation = "Inconsistent performance across criteria"
    elif (
        median_score > 0.5
    ):  # Use median for better representation of typical performance
        heuristic_result.score = SynthesisScore.REVIEW
        heuristic_result.explanation = "Typical performance is borderline"
    else:
        heuristic_result.score = SynthesisScore.REJECTED
        heuristic_result.explanation = "Overall performance below requirements"

    if avg_confidence < 0.6 and heuristic_result.score == SynthesisScore.ACCEPTED:
        heuristic_result.score = SynthesisScore.REVIEW
        heuristic_result.explanation += " (Low confidence in assessment)"

    return heuristic_result
