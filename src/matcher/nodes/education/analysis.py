from langchain import hub
from langchain.chat_models import init_chat_model

from scorecard.models.scorecard import ListScoredCriterion, filter_criteria_by_type
from matcher.state import MainGraphState
from matcher.tools.knowledge_point import get_knowledge_points
from utils.format import format_data


def node_education_analysis(state: MainGraphState) -> MainGraphState:
    criteria = filter_criteria_by_type(state.scorecard, ["EDUCATION"])
    if len(criteria) == 0:
        return {"education_analysis": None}

    prompt = hub.pull("education-analysis")
    db_res = get_knowledge_points(["EDUCATION"])

    model = init_chat_model(
        model="claude-3-5-sonnet-20240620", model_provider="anthropic", temperature=0
    ).with_structured_output(ListScoredCriterion)

    chain = prompt | model

    res = chain.invoke(
        format_data(
            {
                "educations": state.profile.educations,
                "certifications": state.profile.certifications,
                "education_enrichment": state.education_enrichment,
                "knowledge_points": db_res,
                "scorecard": criteria,
            }
        )
    )
    return {"education_analysis": res}
