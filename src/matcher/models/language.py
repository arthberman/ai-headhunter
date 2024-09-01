from enum import Enum

from langchain_core.pydantic_v1 import BaseModel, Field


class ProficiencyEnum(str, Enum):
    native = "native"
    profesionnal = "profesionnal"
    fluent = "fluent"


class LanguageProficiency(BaseModel):
    language: str = Field(
        description="The language in ISO 639-1 code (e.g. 'en' for English, 'fr' for French)"
    )
    proficiency: str = Field(
        description="The proficiency level of the language ('native', 'profesionnal' or 'fluent')"
    )
    reason: str = Field(
        description="The reason for the prediction, brief explanation of the model's decision"
    )
