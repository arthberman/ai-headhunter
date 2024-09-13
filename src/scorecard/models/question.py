from typing import List
from langchain_core.pydantic_v1 import BaseModel
from matcher.models.scorecard import CriteriaType


class Question(BaseModel):
    question: str
    criteria_type: CriteriaType


class ListQuestions(BaseModel):
    questions: List[Question]
