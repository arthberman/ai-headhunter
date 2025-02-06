from statistics import mean, median
from typing import List

from matcher.sub_graph.criterion_matcher.models import ScoredCriterion
from matcher.sub_graph.decision.models import Decision, Outcome
from setup.models.scorecard import Priority, Scorecard
from utils.get_extended_scored_criterion import get_extended_scored_criterion


def compute_must_score(
    scored_criterion: List[ScoredCriterion], scorecard: Scorecard
) -> Decision:
    """Compute the must score heuristically."""
    # Get scored criteria for Must
    scored_must_criteria = get_extended_scored_criterion(
        scored_criterion,
        scorecard,
        priority=Priority.REQUIRED,
    )

    # Calculate scores
    heuristic_result = Decision(outcome=Outcome.REJECTED, explanation="")
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
        heuristic_result = Decision(
            outcome=Outcome.ACCEPTED, explanation="All criteria meet minimum threshold"
        )
    elif min_score <= 0.3:
        heuristic_result = Decision(
            outcome=Outcome.REJECTED,
            explanation="At least one criterion severely underperforms",
        )
    elif score_spread > 0.2:  # High difference between mean and median
        heuristic_result = Decision(
            outcome=Outcome.REVIEW,
            explanation="Inconsistent performance across criteria",
        )
    elif (
        median_score > 0.5
    ):  # Use median for better representation of typical performance
        heuristic_result = Decision(
            outcome=Outcome.REVIEW, explanation="Typical performance is borderline"
        )
    else:
        heuristic_result = Decision(
            outcome=Outcome.REJECTED,
            explanation="Overall performance below requirements",
        )

    if avg_confidence < 0.6 and heuristic_result.outcome == Outcome.ACCEPTED:
        heuristic_result = Decision(
            outcome=Outcome.REVIEW, explanation="Low confidence in assessment"
        )

    return heuristic_result
