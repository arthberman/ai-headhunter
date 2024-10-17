from scorecard.models.scorecard import (
    BaseCriterion,
    ImportanceLevel,
    ScoringDistribution,
)


def prepare_scoring_instructions(
    criterion: BaseCriterion,
) -> str:
    """Prepare scoring instructions for a criterion and return the importance level."""
    instructions = []

    # Add importance level instruction
    instructions.append(
        f"1. Consider the importance level of the criterion: {criterion.importance_level.value}"
    )

    if criterion.importance_level == ImportanceLevel.MUST_HAVE:
        instructions.append(
            "   - This criterion is essential. A score below 0.6 should disqualify the candidate."
        )
    elif criterion.importance_level == ImportanceLevel.IMPORTANT:
        instructions.append(
            "   - This criterion carries significant weight but is not necessarily disqualifying if not fully met."
        )
    elif criterion.importance_level == ImportanceLevel.NICE_TO_HAVE:
        instructions.append(
            "   - This criterion is beneficial but not critical for the role."
        )

    # Add scoring distribution instruction
    if criterion.scoring_distribution:
        instructions.append(
            f"2. Apply the {criterion.scoring_distribution.value} scoring distribution:"
        )

        if criterion.scoring_distribution == ScoringDistribution.BINARY:
            instructions.append(
                "   - Score is either 0 (criterion not met) or 1 (criterion met)."
            )
        elif criterion.scoring_distribution == ScoringDistribution.CONTINUOUS:
            instructions.append(
                "   - Score ranges [not met = 0, low met = 0.3, good met = 0.6 and excellent met = 0.9], allowing for partial fulfillment of the criterion."
            )
        elif criterion.scoring_distribution == ScoringDistribution.GAUSSIAN:
            instructions.append(
                "   - This distribution assumes that the majority of people will score in the middle, with a small percentage scoring very high or very low."
            )

    # Add simplified confidence level instruction
    instructions.append("3. Determine your confidence level:")
    instructions.append(
        "   - LOW = 0.2: When you need to make significant inferences or have limited information to support your evaluation."
    )
    instructions.append(
        "   - MEDIUM = 0.5: When you need to make reasonable inferences based on available information, but you're fairly confident in your assessment."
    )
    instructions.append(
        "   - HIGH = 0.8: When the information is directly available and clearly supports your evaluation."
    )

    # Add criterion-specific information
    instructions.append(f"\nCriterion Description: {criterion.description}")
    if criterion.context:
        instructions.append(f"Context: {criterion.context}")
    instructions.append(f"Type: {criterion.type.value}")

    return "\n".join(instructions)
