from typing import List, Optional

from pydantic import BaseModel, Field

from analysis.models.synthesis import MustSynthesis
from analysis.sub_graph.criterion_analysis.models import ScoredCriterion
from scorecard.models.scorecard import Scorecard
from utils.compute_must_score import compute_must_score
from utils.get_extended_scored_criterion import ExtendedScoredCriterion


class CriterionDetail(BaseModel):
    """Details for a single criterion."""

    category: str
    description: str
    score: float = Field(..., description="Score as percentage (0-100)")
    confidence: float = Field(..., description="Confidence as percentage (0-100)")
    explanation: Optional[str] = None


class ScoredCriteriaOutput(BaseModel):
    """Structured output for scored criteria analysis."""

    must_synthesis: MustSynthesis
    required_criteria: List[CriterionDetail]
    preferred_criteria: List[CriterionDetail]


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

    # Group criteria by priority
    required = [c for c in extended_criteria if c.priority.value == "required"]
    preferred = [c for c in extended_criteria if c.priority.value == "preferred"]

    # Sort each group by score (descending)
    required.sort(key=lambda x: x.score, reverse=True)
    preferred.sort(key=lambda x: x.score, reverse=True)

    # Format criteria lists
    required_criteria = [
        CriterionDetail(
            category=criterion.category,
            description=criterion.description,
            score=round(criterion.score * 100, 1),
            confidence=round(criterion.confidence * 100, 1),
            explanation=criterion.explanation,
        )
        for criterion in required
    ]

    preferred_criteria = [
        CriterionDetail(
            category=criterion.category.value,
            description=criterion.description,
            score=round(criterion.score * 100, 1),
            confidence=round(criterion.confidence * 100, 1),
            explanation=criterion.explanation,
        )
        for criterion in preferred
    ]

    return ScoredCriteriaOutput(
        must_synthesis=must_synthesis,
        required_criteria=required_criteria,
        preferred_criteria=preferred_criteria,
    )
