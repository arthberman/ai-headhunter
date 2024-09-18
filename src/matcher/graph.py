from langgraph.constants import Send
from langgraph.graph import END, START, StateGraph
from langgraph.graph.graph import CompiledGraph

from matcher.nodes.enrichment.education import node_education_enrichment
from matcher.nodes.enrichment.experience import node_experience_enrichment
from matcher.nodes.enrichment.language import node_language_enrichment
from matcher.state import MainGraphState, InputGraphState


def continue_to_school_enrichment(state: MainGraphState):
    if state.profile.educations:
        return [
            Send("node_education_enrichment", {"education": e})
            for e in state.profile.educations
        ]
    else:
        return END


def continue_to_company_enrichment(state: MainGraphState):
    if state.profile.experiences:
        return [
            Send("node_experience_enrichment", {"experience": e})
            for e in state.profile.experiences
        ]
    else:
        return END


def compile_matcher_graph() -> CompiledGraph:
    workflow = StateGraph(MainGraphState, input_schema=InputGraphState)

    workflow.add_node("node_language_enrichment", node_language_enrichment)
    workflow.add_node("node_education_enrichment", node_education_enrichment)
    workflow.add_node("node_experience_enrichment", node_experience_enrichment)

    workflow.add_conditional_edges(
        START,
        continue_to_school_enrichment,
        ["node_education_enrichment", END],
    )
    workflow.add_conditional_edges(
        START,
        continue_to_company_enrichment,
        ["node_experience_enrichment", END],
    )
    workflow.add_edge(START, "node_language_enrichment")
    workflow.add_edge(
        [
            "node_experience_enrichment",
            "node_education_enrichment",
            "node_language_enrichment",
        ],
        END,
    )

    return workflow.compile()
