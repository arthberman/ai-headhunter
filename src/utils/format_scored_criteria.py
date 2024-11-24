from typing import List, Optional

from pydantic import BaseModel, Field

from analysis.models.synthesis import MustSynthesis
from analysis.sub_graph.criterion_analysis.models import ScoredCriterion
from scorecard.models.scorecard import Scorecard
from utils.compute_must_score import compute_must_score
from utils.get_extended_scored_criterion import ExtendedScoredCriterion


class CriterionDetail(BaseModel):
    """Details for a single criterion."""

    type: str
    description: str
    score: float = Field(..., description="Score as percentage (0-100)")
    confidence: float = Field(..., description="Confidence as percentage (0-100)")
    explanation: Optional[str] = None


class ScoredCriteriaOutput(BaseModel):
    """Structured output for scored criteria analysis."""

    must_synthesis: MustSynthesis
    must_have_criteria: List[CriterionDetail]
    nice_to_have_criteria: List[CriterionDetail]


def format_scored_criteria(
    extended_criteria: List[ExtendedScoredCriterion],
    scored_criterion: List[ScoredCriterion],
    scorecard: Scorecard,
) -> ScoredCriteriaOutput:
    """Format extended scored criterion as structured JSON.

    Args:
        extended_criteria: List of extended scored criteria
        scored_criterion: Original scored criteria for must score computation
        scorecard: Scorecard for must score computation

    Returns:
        Pydantic model containing structured criteria analysis
    """
    # Compute must synthesis
    must_synthesis = compute_must_score(scored_criterion, scorecard)

    # Group criteria by importance level
    must_have = [c for c in extended_criteria if c.importance_level == "MUST_HAVE"]
    nice_to_have = [
        c for c in extended_criteria if c.importance_level == "NICE_TO_HAVE"
    ]

    # Sort each group by score (descending)
    must_have.sort(key=lambda x: x.score, reverse=True)
    nice_to_have.sort(key=lambda x: x.score, reverse=True)

    # Format criteria lists
    must_have_criteria = [
        CriterionDetail(
            type=criterion.criterion_type.value,
            description=criterion.description,
            score=round(criterion.score * 100, 1),
            confidence=round(criterion.confidence * 100, 1),
            explanation=criterion.explanation,
        )
        for criterion in must_have
    ]

    nice_to_have_criteria = [
        CriterionDetail(
            type=criterion.criterion_type.value,
            description=criterion.description,
            score=round(criterion.score * 100, 1),
            confidence=round(criterion.confidence * 100, 1),
            explanation=criterion.explanation,
        )
        for criterion in nice_to_have
    ]

    return ScoredCriteriaOutput(
        must_synthesis=must_synthesis,
        must_have_criteria=must_have_criteria,
        nice_to_have_criteria=nice_to_have_criteria,
    )
