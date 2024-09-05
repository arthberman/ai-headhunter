from langchain import hub
from langchain.chat_models import init_chat_model

from matcher.models.scorecard import ListScoredCriterion, filter_criteria_by_type
from matcher.state import MainGraphState
from matcher.tools.knowledge_point import get_knowledge_points
from utils.format import format_data


def node_language_analysis(state: MainGraphState) -> MainGraphState:
    criteria = filter_criteria_by_type(state.scorecard, ["LANGUAGE"])
    if len(criteria) == 0:
        return {"language_analysis": None}

    prompt = hub.pull("language-analysis")
    db_res = get_knowledge_points(["LANGUAGE"])

    model = init_chat_model(
        model="gpt-4o-2024-08-06", model_provider="openai", temperature=0
    ).with_structured_output(ListScoredCriterion)

    chain = prompt | model

    res = chain.invoke(
        format_data(
            {
                "languages": state.profile.languages,
                "language_enrichment": state.language_enrichment,
                "skills": state.profile.skills,
                "certifications": state.profile.certifications,
                "knowledge_points": db_res,
                "scorecard": criteria,
            }
        )
    )
    return {"language_analysis": res}
