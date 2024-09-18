from typing import List

from langchain import hub
from langchain.chat_models import init_chat_model
from pydantic import BaseModel, Field

from matcher.models.language import LanguageProficiency
from matcher.state import MainGraphState
from matcher.tools.knowledge_point import get_knowledge_points


class StructuredOutput(BaseModel):
    language_proficiency: List[LanguageProficiency] = Field(
        description="List of language proficiencies, each containing a language and its corresponding level"
    )


def node_language_enrichment(state: MainGraphState) -> MainGraphState:
    prompt = hub.pull("language-enrichment")
    model = init_chat_model(
        model="gpt-4o-2024-08-06", model_provider="openai", temperature=0
    )

    db_res = get_knowledge_points(["LANGUAGE"])
    chain = prompt | model.with_structured_output(StructuredOutput)
    res = chain.invoke({"profile": state.profile, "knowledge_points": db_res})

    return {"language_enrichment": res.language_proficiency}
