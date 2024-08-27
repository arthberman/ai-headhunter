from langchain import hub
from langchain.chat_models import init_chat_model

from matcher.models.career_path import CareerPathAnalysis
from matcher.state import MainGraphState
from utils.format import format_data


def node_career_path_analysis(state: MainGraphState) -> MainGraphState:
    prompt = hub.pull("career-path-analysis")
    model = init_chat_model(
        model="gpt-4o-mini", model_provider="openai", temperature=0
    )
    chain = prompt | model.with_structured_output(CareerPathAnalysis)

    res = chain.invoke(
        format_data(
            {
                "headline": state.profile.headline,
                "educations": state.profile.educations,
                "experiences": state.profile.experiences,
                "experience_enrichment": state.experience_enrichment,
                "education_enrichment": state.education_enrichment,
                "education": state.profile.educations,
                "job_offer": state.job_offer,
            }
        )
    )
    
    return {"career_path_analysis": res}
