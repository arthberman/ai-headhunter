from langchain import hub
from langchain.chat_models import init_chat_model

from matcher.models.scorecard import ListScoredCriterion, filter_criteria_by_type
from matcher.state import MainGraphState
from matcher.tools.knowledge_point import get_knowledge_points
from utils.format import format_data


def node_hard_skill_analysis(state: MainGraphState) -> MainGraphState:
    criteria = filter_criteria_by_type(state.scorecard, ["HARD_SKILL"])
    if len(criteria) == 0:
        return {"hard_skill_analysis": None}

    prompt = hub.pull("hard-skill-analysis")
    db_res = get_knowledge_points(["HARD_SKILL"])

    model = init_chat_model(
        model="claude-3-5-sonnet-20240620", model_provider="anthropic", temperature=0
    ).with_structured_output(ListScoredCriterion)

    chain = prompt | model
    res = chain.invoke(
        format_data(
            {
                "skills": state.profile.skills,
                "certifications": state.profile.certifications,
                "educations": state.profile.educations,
                "experiences": state.profile.experiences,
                "projects": state.profile.projects,
                "volunteerings": state.profile.volunteerings,
                "language_enrichment": state.language_enrichment,
                "experience_enrichment": state.experience_enrichment,
                "education_enrichment": state.education_enrichment,
                "knowledge_points": db_res,
                "scorecard": criteria,
            }
        )
    )
    return {"hard_skill_analysis": res}
