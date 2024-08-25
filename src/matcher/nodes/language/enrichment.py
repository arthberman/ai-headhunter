from typing import List

from langchain import hub
from langchain.chat_models import init_chat_model
from langchain_core.pydantic_v1 import BaseModel, Field

from matcher.models.language import LanguageProficiency
from matcher.state import MainGraphState


class StructuredOutput(BaseModel):
    language_proficiency: List[LanguageProficiency] = Field(
        description="List of language proficiencies, each containing a language and its corresponding level"
    )


def node_language_enrichment(state: MainGraphState) -> MainGraphState:
    prompt = hub.pull("language-enrichment")
    model = init_chat_model(
        model="gpt-4o-mini", model_provider="openai", temperature=0
    )
    chain = prompt | model.with_structured_output(StructuredOutput)
    res = chain.invoke({"profile": state.profile})

    return {"language_enrichment": res.language_proficiency}
