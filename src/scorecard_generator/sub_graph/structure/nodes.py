from typing import List

from langchain import hub
from langchain.chat_models import init_chat_model

from scorecard_generator.models.scorecard import (
    BaseCriterion,
    ImportanceLevel,
    Scorecard,
)
from scorecard_generator.sub_graph.structure.models import (
    ActionType,
    StructureAction,
    StructureJudgeOutput,
)
from scorecard_generator.sub_graph.structure.state import StructureGraphState


def generate_scorecard_structure(state: StructureGraphState) -> StructureGraphState:
    """Generate a scorecard structure based on the given state."""
    model = init_chat_model(
        model="gpt-4o-2024-08-06",
        model_provider="openai",
        temperature=0,
    )
    structured_model = model.with_structured_output(Scorecard)
    prompt = hub.pull("generate-scorecard-structure")

    chain = prompt | structured_model
    output: Scorecard = chain.invoke(
        {
            "raw_job_posting": state.raw_job_posting,
            "web_context": state.web_context,
            "generated_questions": state.generated_questions,
        }
    )

    return {"scorecard": output}


def iterate_scorecard_structure(state: StructureGraphState) -> StructureGraphState:
    """Iterate the scorecard structure based on the given state."""
    model = init_chat_model(
        model="gpt-4o-2024-08-06",
        model_provider="openai",
        temperature=0,
    )
    structured_model = model.with_structured_output(StructureJudgeOutput)
    prompt = hub.pull("iterate-scorecard-structure")

    chain = prompt | structured_model
    output: StructureJudgeOutput = chain.invoke(
        {
            "previous_scorecard": state.scorecard,
            "raw_job_posting": state.raw_job_posting,
            "web_context": state.web_context,
            "generated_questions": state.generated_questions,
            "human_context": state.human_context,
            "human_feedback": state.human_feedback,
        }
    )

    return {
        "structure_actions": output.structure_actions,
        "human_context": (state.human_context or []) + (state.human_feedback or []),
        "human_feedback": [],
    }


def judge_scorecard_structure(state: StructureGraphState) -> StructureGraphState:
    """Judge the scorecard structure based on the given state."""
    model = init_chat_model(
        model="gpt-4o-2024-08-06",
        model_provider="openai",
        temperature=0,
    )
    structured_model = model.with_structured_output(StructureJudgeOutput)
    prompt = hub.pull("judge-scorecard-structure")

    chain = prompt | structured_model
    output: StructureJudgeOutput = chain.invoke({"scorecard": state.scorecard})

    return {
        "structure_actions": output.structure_actions,
        "is_structure_valid": output.is_structure_valid,
        "recursion_count": state.recursion_count + 1,
    }


def apply_replacements(state: StructureGraphState) -> StructureGraphState:
    """Apply the replacements to the scorecard."""
    scorecard: Scorecard = state.scorecard
    actions: List[StructureAction] = state.structure_actions

    if isinstance(scorecard, dict):
        scorecard = Scorecard(**scorecard)

    for action in actions:
        if action.actionType == ActionType.ADD:
            new_criterion = create_criterion(action)

            if action.importance == ImportanceLevel.MUST_HAVE:
                scorecard.mustHaveCriteria.append(new_criterion)
            elif action.importance == ImportanceLevel.IMPORTANT:
                scorecard.importantCriteria.append(new_criterion)
            elif action.importance == ImportanceLevel.NICE_TO_HAVE:
                scorecard.niceToHaveCriteria.append(new_criterion)

        elif action.actionType == ActionType.DELETE:
            if action.importance == ImportanceLevel.MUST_HAVE:
                scorecard.mustHaveCriteria = [
                    c
                    for c in scorecard.mustHaveCriteria
                    if c.description != action.description
                ]
            elif action.importance == ImportanceLevel.IMPORTANT:
                scorecard.importantCriteria = [
                    c
                    for c in scorecard.importantCriteria
                    if c.description != action.description
                ]
            elif action.importance == ImportanceLevel.NICE_TO_HAVE:
                scorecard.niceToHaveCriteria = [
                    c
                    for c in scorecard.niceToHaveCriteria
                    if c.description != action.description
                ]

    return {"scorecard": scorecard, "structure_actions": [], "is_structure_valid": True}


def create_criterion(action: StructureAction) -> BaseCriterion:
    """Create a criterion based on the given action."""
    return BaseCriterion(
        description=action.description,
        type=action.type,
        scoring_distribution=action.scoring_distribution,
    )
