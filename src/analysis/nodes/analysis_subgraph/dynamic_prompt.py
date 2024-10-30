from analysis.nodes.analysis_subgraph.models import CotQuestions
from scorecard.models.scorecard import (
    BaseCriterion,
    ImportanceLevel,
    ScoringDistribution,
)


def prepare_evaluation_steps(cot_questions: CotQuestions, instructions: str) -> str:
    """Generate evaluation steps with dynamically inserted questions."""
    steps = ["1. Carefully analyze the given criterion to score."]

    # Add questions starting from step 2
    for i, question in enumerate(cot_questions.questions, start=2):
        steps.append(
            f"{i}. Answer the question : {question.text} (purpose: {question.purpose})."
        )

    # Continue with remaining steps
    next_step = len(cot_questions.questions) + 2
    remaining_steps = [
        f"{next_step}. If necessary, use `search_web` to gather additional context available on a web search (maximum 2 call to the `search_web` tool)",
        f"{next_step + 1}. Evaluate how well the candidate meets the criterion based on all gathered information and reasonable inferences.",
        f"{next_step + 2}. Apply the scoring instructions to assign a numerical score:",
        f"{'<scoring_instructions>'}\n{instructions}\n{'</scoring_instructions>'}",  # Escaped using nested f-strings
        f"{next_step + 3}. Determine your confidence level based on whether the information was directly available or inferred.",
        f"{next_step + 4}. Write a brief explanation for your evaluation (max 400 characters), including:",
        "   - Key factors that influenced your scoring",
        "   - Any inferences you made and how they affected your score and confidence level",
        f"{next_step + 5}. Use `ScoredCriterion` tool to submit your final score, explanation, and confidence level.",
    ]

    steps.extend(remaining_steps)

    return "\n".join(steps)


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

    return "\n".join(instructions)
