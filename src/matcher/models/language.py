from enum import Enum

from pydantic import BaseModel, Field


class ProficiencyEnum(Enum):
    """Proficiency level of the language."""

    NATIVE = "native"
    PROFESSIONAL = "professional"
    FLUENT = "fluent"


class LanguageProficiency(BaseModel):
    """Language proficiency of the candidate."""

    language: str = Field(
        description="The language in ISO 639-1 code (e.g. 'en' for English, 'fr' for French)"
    )
    proficiency: ProficiencyEnum = Field(
        description="The proficiency level of the language ('native', 'professional' or 'fluent')"
    )
    explanation: str = Field(
        description="The explanation for the prediction, brief explanation of the model's decision"
    )
