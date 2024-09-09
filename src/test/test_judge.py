# %%
from typing import List, Optional, TypedDict, Union
from enum import Enum

from langchain import hub
from langchain.chat_models import init_chat_model
from langchain_core.pydantic_v1 import Field
from langgraph.graph import END, StateGraph, START

from matcher.models.scorecard import (
    CriteriaType,
    ImportanceLevel,
    ImportantCriterion,
    MustHaveCriterion,
    NiceToHaveCriterion,
    Scorecard,
)


# New data models for structure judge and content judge
class ActionType(str, Enum):
    DELETE = "DELETE"
    ADD = "ADD"
    MOVE_TO_NICE_TO_HAVE = "MOVE_TO_NICE_TO_HAVE"


class StructureAction(TypedDict):
    actionType: ActionType
    importance: ImportanceLevel
    type: CriteriaType
    description: str


class ContentAction(TypedDict):
    action: ActionType
    from_importance: ImportanceLevel
    type: CriteriaType
    description: str


class StructureJudgeOutput(TypedDict):
    is_structure_valid: bool
    structure_actions: List[StructureAction] | None


class ContentJudgeOutput(TypedDict):
    is_content_valid: bool
    content_actions: List[ContentAction] | None


# Add a new class for the missing judge output
class MissingJudgeOutput(TypedDict):
    is_valid: bool
    actions: List[StructureAction] | None


class GraphState(TypedDict):
    raw_job_posting: str
    scorecard: Optional[Scorecard]
    structure_actions: Optional[List[StructureAction] | None]
    content_actions: Optional[List[ContentAction] | None]
    missing_actions: Optional[List[StructureAction] | None]
    is_structure_valid: Optional[bool]
    is_content_valid: Optional[bool]
    is_missing_valid: Optional[bool]
    count_missing_judge: int = Field(default=0)
    count_content_judge: int = Field(default=0)
    count_structure_judge: int = Field(default=0)


# Define the nodes
def generate_scorecard(state: GraphState) -> GraphState:
    model = init_chat_model(
        model="gpt-4o-2024-08-06",
        model_provider="openai",
        temperature=0,
    )
    structured_model = model.with_structured_output(Scorecard)
    prompt = hub.pull("parser-scorecard")

    chain = prompt | structured_model
    output: Scorecard = chain.invoke(state["raw_job_posting"])

    return {"scorecard": output}


def judge_scorecard_structure(state: GraphState) -> GraphState:
    model = init_chat_model(
        model="gpt-4o-2024-08-06",
        model_provider="openai",
        temperature=0,
    )
    structured_model = model.with_structured_output(StructureJudgeOutput)
    prompt = hub.pull("judge-scorecard-structure")

    chain = prompt | structured_model
    output: StructureJudgeOutput = chain.invoke({"scorecard": state["scorecard"]})

    count = state.get("count_structure_judge", 0)
    return {**output, "count_structure_judge": count + 1}


def judge_scorecard_content(state: GraphState) -> GraphState:
    model = init_chat_model(
        model="gpt-4o-2024-08-06",
        model_provider="openai",
        temperature=0,
    )
    structured_model = model.with_structured_output(ContentJudgeOutput)
    prompt = hub.pull("judge-scorecard-content")

    chain = prompt | structured_model
    output: ContentJudgeOutput = chain.invoke({"scorecard": state["scorecard"]})

    # Use get() method with a default value of 0
    count = state.get("count_content_judge", 0)
    return {**output, "count_content_judge": count + 1}


def judge_scorecard_missing(state: GraphState) -> GraphState:
    model = init_chat_model(
        model="gpt-4o-2024-08-06",
        model_provider="openai",
        temperature=0,
    )
    structured_model = model.with_structured_output(MissingJudgeOutput)
    prompt = hub.pull("judge-scorecard-missing")

    chain = prompt | structured_model
    output: MissingJudgeOutput = chain.invoke(
        {"raw_job_posting": state["raw_job_posting"], "scorecard": state["scorecard"]}
    )

    count = state.get("count_missing_judge", 0)

    return {
        "is_missing_valid": output["is_valid"],
        "missing_actions": output["actions"],
        "count_missing_judge": count + 1,
    }


def apply_replacements(state: GraphState) -> GraphState:
    scorecard: Scorecard = state["scorecard"]
    actions: List[StructureAction] = state["structure_actions"]

    if isinstance(scorecard, dict):
        scorecard = Scorecard(**scorecard)

    for action in actions:
        if action["actionType"] == ActionType.ADD:
            new_criterion = create_criterion(action)

            if action["importance"] == ImportanceLevel.MUST_HAVE:
                scorecard.mustHaveCriteria.criteria.append(new_criterion)
            elif action["importance"] == ImportanceLevel.IMPORTANT:
                scorecard.importantCriteria.criteria.append(new_criterion)
            elif action["importance"] == ImportanceLevel.NICE_TO_HAVE:
                scorecard.niceToHaveCriteria.criteria.append(new_criterion)

        elif action["actionType"] == ActionType.DELETE:
            if action["importance"] == ImportanceLevel.MUST_HAVE:
                scorecard.mustHaveCriteria.criteria = [
                    c
                    for c in scorecard.mustHaveCriteria.criteria
                    if c.description != action["description"]
                ]
            elif action["importance"] == ImportanceLevel.IMPORTANT:
                scorecard.importantCriteria.criteria = [
                    c
                    for c in scorecard.importantCriteria.criteria
                    if c.description != action["description"]
                ]
            elif action["importance"] == ImportanceLevel.NICE_TO_HAVE:
                scorecard.niceToHaveCriteria.criteria = [
                    c
                    for c in scorecard.niceToHaveCriteria.criteria
                    if c.description != action["description"]
                ]

    recalculate_weights(scorecard.mustHaveCriteria.criteria)
    recalculate_weights(scorecard.importantCriteria.criteria)

    return {"scorecard": scorecard, "structure_actions": [], "is_structure_valid": True}


def apply_content_replacements(state: GraphState) -> GraphState:
    scorecard: Scorecard = state["scorecard"]
    actions: List[ContentAction] = state["content_actions"]

    if isinstance(scorecard, dict):
        scorecard = Scorecard(**scorecard)

    for action in actions:
        if action["action"] == ActionType.MOVE_TO_NICE_TO_HAVE:
            criterion = None
            if action["from_importance"] == ImportanceLevel.MUST_HAVE:
                criterion = next(
                    (
                        c
                        for c in scorecard.mustHaveCriteria.criteria
                        if c.description == action["description"]
                    ),
                    None,
                )
                if criterion:
                    scorecard.mustHaveCriteria.criteria.remove(criterion)
            elif action["from_importance"] == ImportanceLevel.IMPORTANT:
                criterion = next(
                    (
                        c
                        for c in scorecard.importantCriteria.criteria
                        if c.description == action["description"]
                    ),
                    None,
                )
                if criterion:
                    scorecard.importantCriteria.criteria.remove(criterion)

            if criterion:
                new_criterion = NiceToHaveCriterion(
                    description=criterion.description,
                    type=criterion.type,
                    importance=ImportanceLevel.NICE_TO_HAVE,
                    maxBonusPoint=1.0,
                )
                scorecard.niceToHaveCriteria.criteria.append(new_criterion)

    recalculate_weights(scorecard.mustHaveCriteria.criteria)
    recalculate_weights(scorecard.importantCriteria.criteria)

    return {"scorecard": scorecard, "content_actions": None, "is_content_valid": True}


def apply_missing_replacements(state: GraphState) -> GraphState:
    scorecard: Scorecard = state["scorecard"]
    actions: List[StructureAction] = state["missing_actions"]

    if isinstance(scorecard, dict):
        scorecard = Scorecard(**scorecard)

    for action in actions:
        if action["actionType"] == ActionType.ADD:
            new_criterion = create_criterion(action)

            if action["importance"] == ImportanceLevel.MUST_HAVE:
                scorecard.mustHaveCriteria.criteria.append(new_criterion)
            elif action["importance"] == ImportanceLevel.IMPORTANT:
                scorecard.importantCriteria.criteria.append(new_criterion)

    recalculate_weights(scorecard.mustHaveCriteria.criteria)
    recalculate_weights(scorecard.importantCriteria.criteria)

    return {"scorecard": scorecard, "missing_actions": None, "is_missing_valid": True}


def create_criterion(
    action: StructureAction,
) -> Union[MustHaveCriterion, ImportantCriterion, NiceToHaveCriterion]:
    base_criterion = {
        "description": action["description"],
        "type": action["type"],
        "importance": action["importance"],
    }

    if action["importance"] == ImportanceLevel.MUST_HAVE:
        return MustHaveCriterion(**base_criterion, weight=0.0)
    elif action["importance"] == ImportanceLevel.IMPORTANT:
        return ImportantCriterion(**base_criterion, weight=0.0)
    elif action["importance"] == ImportanceLevel.NICE_TO_HAVE:
        return NiceToHaveCriterion(**base_criterion, maxBonusPoint=1.0)


def recalculate_weights(criteria: List[Union[MustHaveCriterion, ImportantCriterion]]):
    total_criteria = len(criteria)
    if total_criteria > 0:
        new_weight = 1.0 / total_criteria
        for criterion in criteria:
            criterion.weight = new_weight


# Define the graph
workflow = StateGraph(GraphState)

# Add nodes to the graph
workflow.add_node("generate_scorecard", generate_scorecard)
workflow.add_node("judge_scorecard_structure", judge_scorecard_structure)
workflow.add_node("judge_scorecard_content", judge_scorecard_content)
workflow.add_node("judge_scorecard_missing", judge_scorecard_missing)
workflow.add_node("apply_structure_replacements", apply_replacements)
workflow.add_node("apply_content_replacements", apply_content_replacements)
workflow.add_node("apply_missing_replacements", apply_missing_replacements)

# Define the edges
workflow.add_edge(START, "generate_scorecard")
workflow.add_edge("generate_scorecard", "judge_scorecard_structure")

workflow.add_conditional_edges(
    "judge_scorecard_structure",
    lambda x: x["is_structure_valid"] or x["count_structure_judge"] >= 3,
    {True: "judge_scorecard_content", False: "apply_structure_replacements"},
)

workflow.add_edge("apply_structure_replacements", "judge_scorecard_structure")

workflow.add_conditional_edges(
    "judge_scorecard_content",
    lambda x: x["is_content_valid"] or x["count_content_judge"] >= 2,
    {True: "judge_scorecard_missing", False: "apply_content_replacements"},
)

workflow.add_edge("apply_content_replacements", "judge_scorecard_missing")

workflow.add_conditional_edges(
    "judge_scorecard_missing",
    lambda x: x["is_missing_valid"] or x["count_missing_judge"] >= 2,
    {True: END, False: "apply_missing_replacements"},
)

workflow.add_edge("apply_missing_replacements", "judge_scorecard_structure")

# Compile the graph
app = workflow.compile()
