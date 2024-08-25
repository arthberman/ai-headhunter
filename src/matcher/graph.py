from langgraph.constants import Send
from langgraph.graph import END, START, StateGraph
from langgraph.graph.graph import CompiledGraph

from matcher.nodes.career_path.analysis import node_career_path_analysis
from matcher.nodes.education.analysis import node_education_analysis
from matcher.nodes.education.enrichment import node_education_enrichment
from matcher.nodes.experience.analysis import node_experience_analysis
from matcher.nodes.experience.enrichment import node_experience_enrichment
from matcher.nodes.hard_skill.analysis import node_hard_skill_analysis
from matcher.nodes.language.analysis import node_language_analysis
from matcher.nodes.language.enrichment import node_language_enrichment
from matcher.nodes.soft_skill.analysis import node_soft_skill_analysis
from matcher.state import MainGraphState


def continue_to_school_enrichment(state: MainGraphState):
    return [
        Send("node_education_enrichment", {"education": e})
        for e in state.profile.educations
    ]


def continue_to_company_enrichment(state: MainGraphState):
    return [
        Send("node_experience_enrichment", {"experience": e})
        for e in state.profile.experiences
    ]


def test(state: MainGraphState) -> MainGraphState:
    return state


from utils.score_compute import calculate_final_score


def synthesis(state: MainGraphState) -> MainGraphState:
    score = calculate_final_score(state)
    return score


def compile_graph() -> CompiledGraph:
    workflow = StateGraph(MainGraphState)

    workflow.add_node("node_language_enrichment", node_language_enrichment)
    workflow.add_node("node_career_path_analysis", node_career_path_analysis)
    workflow.add_node("node_education_analysis", node_education_analysis)
    workflow.add_node("node_experience_analysis", node_experience_analysis)
    workflow.add_node("node_education_enrichment", node_education_enrichment)
    workflow.add_node("node_experience_enrichment", node_experience_enrichment)
    workflow.add_node("node_soft_skill_analysis", node_soft_skill_analysis)
    workflow.add_node("node_hard_skill_analysis", node_hard_skill_analysis)
    workflow.add_node("node_language_analysis", node_language_analysis)

    workflow.add_node("analysis", test)
    workflow.add_node("synthesis", synthesis)

    workflow.add_conditional_edges(
        START, continue_to_school_enrichment, ["node_education_enrichment"]
    )
    workflow.add_conditional_edges(
        START, continue_to_company_enrichment, ["node_experience_enrichment"]
    )
    workflow.add_edge(START, "node_language_enrichment")
    workflow.add_edge(
        [
            "node_experience_enrichment",
            "node_education_enrichment",
            "node_language_enrichment",
        ],
        "node_career_path_analysis",
    )
    workflow.add_conditional_edges(
        "node_career_path_analysis",
        lambda state: state.career_path_analysis.logicalMove,
        {
            True: "analysis",
            False: "analysis",
        },
    )

    workflow.add_edge("analysis", "node_education_analysis")
    workflow.add_edge("analysis", "node_experience_analysis")
    workflow.add_edge("analysis", "node_hard_skill_analysis")
    workflow.add_edge("analysis", "node_soft_skill_analysis")
    workflow.add_edge("analysis", "node_language_analysis")

    workflow.add_edge("node_education_analysis", "synthesis")
    workflow.add_edge("node_experience_analysis", "synthesis")
    workflow.add_edge("node_hard_skill_analysis", "synthesis")
    workflow.add_edge("node_soft_skill_analysis", "synthesis")
    workflow.add_edge("node_language_analysis", "synthesis")

    workflow.add_edge("synthesis", END)

    return workflow.compile()
