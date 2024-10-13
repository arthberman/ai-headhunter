from enum import Enum

from pydantic import BaseModel, Field


class ProficiencyEnum(str, Enum):
    """Proficiency level of the language."""

    NATIVE = "native"
    PROFESIONNAL = "profesionnal"
    FLUENT = "fluent"


class LanguageProficiency(BaseModel):
    """Language proficiency of the candidate."""

    language: str = Field(
        description="The language in ISO 639-1 code (e.g. 'en' for English, 'fr' for French)"
    )
    proficiency: str = Field(
        description="The proficiency level of the language ('native', 'profesionnal' or 'fluent')"
    )
    reason: str = Field(
        description="The reason for the prediction, brief explanation of the model's decision"
    )
