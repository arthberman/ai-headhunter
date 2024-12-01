from enum import Enum
from typing import List

from pydantic import BaseModel, Field, field_validator, model_validator


class ExtendedCriterionType(str, Enum):
    """Extended criterion type for questions."""

    # Base criteria
    EDUCATION = "education"
    EXPERIENCE = "experience"
    LANGUAGE = "language"
    HARD_SKILL = "hard_skill"
    SOFT_SKILL = "soft_skill"
    INDUSTRY_KNOWLEDGE = "industry_knowledge"
    ADDITIONAL_QUALIFICATION = "additional_qualification"

    # Additional criteria
    JOB_LOCATION_REMOTE_POLICY = "job_location_remote_policy"
    CANDIDATE_AGE_RANGE = "candidate_age_range"
    SALARY_RANGE = "salary_range"


class Question(BaseModel):
    """Question about uncertainty in the job posting."""

    question: str = Field(
        ...,
        description="Question about uncertainty in the job posting, max 130 characters",
        max_length=130,
    )
    prefill_answer: List[str] = Field(
        ..., description="Answers to prefill in the question, max 60 characters each"
    )
    criteria_type: ExtendedCriterionType = Field(
        ..., description="Criteria type that the question is about"
    )

    @field_validator("prefill_answer")
    def validate_prefill_answer(cls, v):
        """Validate that there are at least 1 prefill answers per question, and that each prefill answer is not more than 60 characters."""
        if len(v) < 1:
            raise ValueError("There must be at least 1 prefill answer per question")
        for answer in v:
            if len(answer) > 60:
                raise ValueError("Each prefill answer must not exceed 60 characters")
        return v


class ListQuestions(BaseModel):
    """List of questions about uncertainty in the job posting (min 10 questions)."""

    questions: List[Question] = Field(
        ...,
        description="List of questions about uncertainty in the job posting (min 10 questions)",
        min_length=10,
    )

    @model_validator(mode="after")
    def validate_questions(self) -> "ListQuestions":
        """Validate that there is at least one question for Language, Education, and Experience, and that there are at least 10 questions in total."""
        if len(self.questions) < 10:
            raise ValueError("There must be at least 10 questions")

        criteria_types = [q.criteria_type for q in self.questions]
        required_types = [
            ExtendedCriterionType.LANGUAGE,
            ExtendedCriterionType.EDUCATION,
            ExtendedCriterionType.EXPERIENCE,
            ExtendedCriterionType.JOB_LOCATION_REMOTE_POLICY,
            ExtendedCriterionType.CANDIDATE_AGE_RANGE,
            ExtendedCriterionType.SALARY_RANGE,
        ]

        for required_type in required_types:
            if required_type not in criteria_types:
                raise ValueError(
                    f"There must be at least 1 question about {required_type}"
                )

        return self
