from langchain import hub
from langchain.chat_models import init_chat_model

from matcher.models.profile import ProfileEducation
from matcher.models.school import SchoolInfo
from matcher.state import MainGraphState, EducationState
from matcher.tools.education import get_school, tavily_tool, update_school


def node_education_enrichment(state: EducationState) -> MainGraphState:
    education: ProfileEducation = state["education"]
    db_res = get_school(education.school, education.linkedin_url)
    if db_res is not None:
        return {"education_enrichment": [db_res]}

    tavily_res = tavily_tool.invoke({"query": f"school {education.school}"})
    prompt = hub.pull("education-enrichment")
    model = init_chat_model(
        model="gpt-4o-mini", model_provider="openai", temperature=0
    ).with_structured_output(SchoolInfo)
    chain = prompt | model
    res = chain.invoke(
        {
            "web_browsing_result": tavily_res,
            "school": education.school,
            "school_description": education.description,
            "linkedin_url": education.linkedin_url,
        }
    )

    school_info = SchoolInfo(**res.dict())
    if school_info.uncertainty == False:
        update_school(school_info)
        return {"education_enrichment": [school_info]}

    return {"education_enrichment": []}
