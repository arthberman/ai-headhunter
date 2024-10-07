from enum import Enum

from pydantic import BaseModel, Field


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
