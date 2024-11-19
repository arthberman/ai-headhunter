from analysis.sub_graph.criterion_analysis.models import CotQuestions
from scorecard.models.scorecard import (
    BaseCriterion,
    ImportanceLevel,
    ScoringDistribution,
)


def prepare_evaluation_steps(cot_questions: CotQuestions, instructions: str) -> str:
    """Generate evaluation steps with dynamically inserted questions."""
    steps = []
    steps.append("1. Carefully analyze the given criterion to score.")

    # Add questions section with letter formatting
    steps.append(
        "2. To help you evaluate the criterion to score, you can try to answer the following questions :"
    )

    # Add individual questions with letter formatting and indentation
    for i, question in enumerate(cot_questions.questions):
        letter = chr(97 + i)  # Convert 0,1,2... to a,b,c...
        steps.append(f"     {letter}. {question.text} (purpose: {question.purpose}).")

    # Continue with remaining steps
    next_step = 3
    remaining_steps = [
        f"{next_step}. If necessary, use `search_web` to gather additional context available on a web search (maximum 2 call to the `search_web` tool)",
        f"{next_step + 1}. Evaluate how well the candidate meets the criterion based on all gathered information and reasonable inferences.",
        f"{next_step + 2}. Apply the scoring instructions to assign a numerical score:",
        f"{instructions}",
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
    current_letter = "a"

    # Add importance level instruction
    instructions.append(
        f"{current_letter}. Consider the importance level of the criterion: {criterion.importance_level.value}"
    )

    if criterion.importance_level == ImportanceLevel.MUST_HAVE:
        instructions.append(
            "   - This criterion is essential. A score strictly below 0.6 should disqualify the candidate."
        )
    elif criterion.importance_level == ImportanceLevel.NICE_TO_HAVE:
        instructions.append(
            "   - This criterion is beneficial but not critical for the role."
        )

    current_letter = chr(ord(current_letter) + 1)  # Increment to 'b'

    # Add scoring distribution instruction
    if criterion.scoring_distribution:
        instructions.append(
            f"{current_letter}. Apply the {criterion.scoring_distribution.value} scoring distribution:"
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
                "   - Score ranges [low met = 0.2, average met = 0.5 and excellent met = 0.8], this distribution assumes that the majority of people will score in the middle [average met 0.5], with a small percentage scoring very high or very low."
            )

        current_letter = chr(ord(current_letter) + 1)  # Increment to next letter

    # Add experience-specific instructions if criterion type is EXPERIENCE
    if criterion.type == "EXPERIENCE":
        instructions.append(
            f"{current_letter}. When evaluating experience-based criteria, carefully analyze the candidate's career trajectory:"
        )
        instructions.append(
            "   i. Review experiences chronologically (from oldest to newest) to identify clear career path changes"
        )
        instructions.append("   ii. Pay special attention to:")
        instructions.append(
            "      - Skill transitions: Moving from one domain/expertise to another"
        )
        instructions.append(
            "      - Role transitions: Shifting between different types of positions"
        )
        instructions.append(
            "      - Duration of transitions: Whether changes are temporary or represent a sustained new direction"
        )
        instructions.append(
            "   iii. For MUST_HAVE criteria (primary skills for the role):"
        )
        instructions.append(
            "      - If the candidate has permanently moved to different domains, earlier experience becomes less relevant, even if substantial"
        )
        instructions.append(
            "   iv. For NICE_TO_HAVE criteria (secondary/complementary skills):"
        )
        instructions.append(
            "      - Past experience remains valuable for evaluation even if not recently practiced"
        )
        instructions.append("\n   Examples:")
        instructions.append("   Technical Case (MUST_HAVE Java Backend experience):")
        instructions.append(
            "   Career path: Java Backend (3y) → Flutter (2y) → React Native (Current, 3y)"
        )
        instructions.append(
            "   Analysis: Clear trajectory away from backend development into mobile, indicating Java experience is not relevant anymore"
        )
        instructions.append(
            "\n   Same Technical Case (NICE_TO_HAVE Java Backend experience):"
        )
        instructions.append(
            "   Career path: Java Backend (3y) → Flutter (2y) → React Native (Current, 3y)"
        )
        instructions.append(
            "   Analysis: Past Java experience is valuable as complementary knowledge, even if candidate moved to mobile development"
        )
        instructions.append("\n   Non-Technical Case (MUST_HAVE Sales experience):")
        instructions.append(
            "   Career path: Sales Representative (4y) → Sales Manager (1y) → HR Manager (2y) → HR Director (Current, 3y)"
        )
        instructions.append(
            "   Analysis: Despite strong sales background, clear trajectory shows commitment to HR career path, making sales experience less relevant"
        )

        current_letter = chr(ord(current_letter) + 1)  # Increment to next letter

    # Add simplified confidence level instruction
    instructions.append(f"{current_letter}. Determine your confidence level:")
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
