from typing import List

from analysis.sub_graph.criterion_analysis.models import ScoredCriterion
from scorecard.models.scorecard import Scorecard
from utils.compute_must_score import compute_must_score
from utils.get_extended_scored_criterion import ExtendedScoredCriterion


def format_scored_criteria(
    extended_criteria: List[ExtendedScoredCriterion],
    scored_criterion: List[ScoredCriterion],
    scorecard: Scorecard,
) -> str:
    """Format extended scored criterion in a readable format.

    Args:
        extended_criteria: List of extended scored criteria
        scored_criterion: Original scored criteria for must score computation
        scorecard: Scorecard for must score computation

    Returns:
        Formatted string representation
    """
    output = []
    output.append("Scored Criteria Analysis")

    # Compute and add must synthesis
    must_synthesis = compute_must_score(scored_criterion, scorecard)
    output.append("\nMust-Have Analysis:")
    output.append(f"Score: {must_synthesis.score.value}")
    output.append(f"Explanation: {must_synthesis.explanation}")
    output.append("")

    # Group criteria by importance level
    must_have = [c for c in extended_criteria if c.importance_level == "MUST_HAVE"]
    nice_to_have = [
        c for c in extended_criteria if c.importance_level == "NICE_TO_HAVE"
    ]

    # Sort each group by score (descending)
    must_have.sort(key=lambda x: x.score, reverse=True)
    nice_to_have.sort(key=lambda x: x.score, reverse=True)

    # Format MUST_HAVE criteria
    if must_have:
        output.append("MUST-HAVE Criteria:")
        for criterion in must_have:
            score_percentage = f"{criterion.score * 100:.1f}%"
            confidence_percentage = f"{criterion.confidence * 100:.1f}%"
            output.append(
                f"• [{criterion.criterion_type.value}] {criterion.description} "
                f"(Score: {score_percentage} | Confidence: {confidence_percentage})"
            )
            if criterion.explanation:
                output.append(f"    ↳ {criterion.explanation}")
            output.append("")

    # Format NICE_TO_HAVE criteria
    if nice_to_have:
        output.append("NICE-TO-HAVE Criteria:")
        for criterion in nice_to_have:
            score_percentage = f"{criterion.score * 100:.1f}%"
            confidence_percentage = f"{criterion.confidence * 100:.1f}%"
            output.append(
                f"• [{criterion.criterion_type.value}] {criterion.description} "
                f"(Score: {score_percentage} | Confidence: {confidence_percentage})"
            )
            if criterion.explanation:
                output.append(f"    ↳ {criterion.explanation}")
            output.append("")

    return "\n".join(output).rstrip()
