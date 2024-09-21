from typing import List, Optional

from pydantic import BaseModel, Field

from scorecard_generator.models.scorecard import CriterionType


class Question(BaseModel):
    question: str = Field(..., description="Question to ask the user")
    criteria_type: CriterionType = Field(
        ..., description="Criteria type that the question is about"
    )
    answer: Optional[str] = Field(None, description="Answer to the question")


class ListQuestions(BaseModel):
    questions: List[Question] = Field(
        ..., description="List of questions to ask the user"
    )
