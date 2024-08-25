from langchain import hub
from langchain.chat_models import init_chat_model

from matcher.models.company import CompanyInfo
from matcher.models.profile import ProfileExperience
from matcher.state import ExperienceState, MainGraphState
from matcher.tools.experience import get_company, tavily_tool, update_company


def node_experience_enrichment(state: ExperienceState) -> MainGraphState:
    experience: ProfileExperience = state["experience"]

    db_res = get_company(experience.company, experience.linkedin_url)
    if db_res is not None:
        return {"experience_enrichment": [db_res]}

    tavily_res = tavily_tool.invoke({"query": f"company {experience.company}"})
    prompt = hub.pull("experience-enrichment")
    model = init_chat_model(
        model="gpt-4o-mini", model_provider="openai", temperature=0
    ).with_structured_output(CompanyInfo)

    chain = prompt | model
    res = chain.invoke(
        {
            "web_browsing_result": tavily_res,
            "company": experience.company,
            "company_title": experience.title,
            "company_description": experience.description,
            "linkedin_url": experience.linkedin_url,
        }
    )

    company_info = CompanyInfo(**res.dict())
    if company_info.uncertainty == False:
        update_company(company_info)
        return {"experience_enrichment": [company_info]}

    return {"experience_enrichment": []}
