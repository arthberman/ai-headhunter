from typing import Dict

from matcher.models.scorecard import ImportanceLevel, Scorecard
from matcher.state import MainGraphState


def calculate_final_score(state: MainGraphState) -> Dict[str, float]:
    if not state.scorecard:
        return {
            "must_have_score": 0.0,
            "important_score": 0.0,
            "nice_to_have_score": 1.0,
            "final_score_score": 0.0,
        }

    scorecard: Scorecard = state.scorecard

    def get_score_by_id(criterion_id: str) -> float:
        for analysis in [
            state.education_analysis,
            state.experience_analysis,
            state.language_analysis,
            state.soft_skill_analysis,
            state.hard_skill_analysis,
        ]:
            if analysis and analysis.scored_criteria:
                for criterion in analysis.scored_criteria:
                    if criterion.id == criterion_id:
                        return criterion.score
        return 0.0

    def calculate_must_have_score(section) -> float:
        total_score = 0.0
        for criterion in section.criteria:
            score = get_score_by_id(criterion.id)
            total_score += score * criterion.weight
        return total_score

    def calculate_important_score(section) -> float:
        return sum(
            get_score_by_id(criterion.id) * criterion.weight
            for criterion in section.criteria
        )

    def calculate_nice_to_have_multiplier(section) -> float:
        total_bonus = sum(
            min(
                get_score_by_id(criterion.id),
                criterion.max_bonus_point,
            )
            for criterion in section.criteria
        )
        max_possible_bonus = sum(
            criterion.max_bonus_point for criterion in section.criteria
        )
        return 1 + (total_bonus / max_possible_bonus) * 0.2  # 20% maximum increase

    must_have_score = 0.0
    important_score = 0.0
    nice_to_have_multiplier = 1.0

    for section in scorecard.sections:
        if section.importance_level == ImportanceLevel.MUST_HAVE:
            must_have_score = calculate_must_have_score(section)
        elif section.importance_level == ImportanceLevel.IMPORTANT:
            important_score = calculate_important_score(section)
        elif section.importance_level == ImportanceLevel.NICE_TO_HAVE:
            nice_to_have_multiplier = calculate_nice_to_have_multiplier(section)

    base_score = (
        scorecard.must_have_weight * must_have_score
        + scorecard.important_weight * important_score
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


# Example usage:
# scores = calculate_final_score(state)
# print(f"Must Have Score: {scores['must_have']:.2f}")
# print(f"Important Score: {scores['important']:.2f}")
# print(f"Nice to Have Multiplier: {scores['nice_to_have']:.2f}")
# print(f"Final Score: {scores['final_score']:.2f}")
