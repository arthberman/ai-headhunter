from typing import Dict

from scorecard.models.scorecard import ImportanceLevel, Scorecard
from matcher.state import MainGraphState


def calculate_final_score(state: MainGraphState) -> Dict[str, float]:
    if not state.scorecard:
        return {
            "must_have_score": 0.0,
            "important_score": 0.0,
            "nice_to_have_multiplier": 1.0,
            "final_score": 0.0,
        }

    scorecard: Scorecard = state.scorecard

    def get_score_by_id(criterion_id: str) -> float:
        for analysis in [
            state.education_analysis,
            state.experience_analysis,
            state.language_analysis,
            state.soft_skill_analysis,
            state.hard_skill_analysis,
            state.industry_knowledge_analysis,
            state.additional_qualification_analysis,
        ]:
            if analysis and analysis.scoredCriteria:
                for criterion in analysis.scoredCriteria:
                    if criterion.id == criterion_id:
                        return criterion.score
        return 0.0

    def calculate_must_have_score() -> float:
        total_score = 0.0
        for criterion in scorecard.mustHaveCriteria.criteria:
            score = get_score_by_id(criterion.id)
            total_score += score * criterion.weight
        return total_score

    def calculate_important_score() -> float:
        return sum(
            get_score_by_id(criterion.id) * criterion.weight
            for criterion in scorecard.importantCriteria.criteria
        )

    def calculate_nice_to_have_multiplier() -> float:
        total_bonus = sum(
            min(
                get_score_by_id(criterion.id),
                criterion.maxBonusPoint,
            )
            for criterion in scorecard.niceToHaveCriteria.criteria
        )
        max_possible_bonus = sum(
            criterion.maxBonusPoint
            for criterion in scorecard.niceToHaveCriteria.criteria
        )
        return 1 + (total_bonus / max_possible_bonus) * 0.2  # 20% maximum increase

    must_have_score = calculate_must_have_score()
    important_score = calculate_important_score()
    nice_to_have_multiplier = calculate_nice_to_have_multiplier()

    base_score = (
        scorecard.mustHaveWeight * must_have_score
        + scorecard.importantWeight * important_score
    )

    # Adjust the nice_to_have_multiplier to ensure final score doesn't exceed 1
    max_multiplier = 1 / base_score if base_score > 0 else float("inf")
    adjusted_multiplier = 1 + (nice_to_have_multiplier - 1) * min(
        1, (max_multiplier - 1) / 0.2
    )

    final_score = base_score * adjusted_multiplier

    return {
        "must_have_score": must_have_score,
        "important_score": important_score,
        "nice_to_have_multiplier": nice_to_have_multiplier,
        "final_score": final_score,
    }
