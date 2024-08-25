from typing import List

from langchain import hub
from langchain.chat_models import init_chat_model
from langchain_core.pydantic_v1 import BaseModel, Field

from matcher.state import MainGraphState


class StructuredOutput(BaseModel):
    questions: List[str] = Field(
        description="list of 5-10 specific, targeted questions for the experience background analysis agent"
    )
    summary: str = Field(
        description="brief summary of the job offer's experiences requirements"
    )


def node_experience_requirements(state: MainGraphState) -> MainGraphState:
    prompt = hub.pull("experience-requirements")
    model = init_chat_model(model="gpt-4o-mini", model_provider="openai", temperature=0)
    chain = prompt | model.with_structured_output(StructuredOutput)

    res = chain.invoke({"job_offer": state["job_offer"]})
    return {
        "experience_requirements_questions": res.questions,
        "experience_requirements_summary": res.summary,
    }
