import uuid
from typing import List

from langgraph.types import interrupt
from pydantic import BaseModel, Field

from setup.models.question import ListQuestions
from setup.state import ScorecardGraphState


class Answer(BaseModel):
    """An answer to a question."""

    question_id: uuid.UUID = Field(..., description="The ID of the question")
    final_answer: str = Field(..., description="The answer to the question")


class Response(BaseModel):
    """Expected response structure from human answer questions interrupt."""

    answers: List[Answer] = Field(..., description="The answers to the questions")


async def node_human_answer_questions(
    state: ScorecardGraphState,
) -> ScorecardGraphState:
    """Human answer questions."""
    questions = state.questions.questions.copy()

    result = Response.model_validate(
        interrupt(
            {
                "event_name": "answer_questions",
                "questions": questions,
            }
        )
    )

    questions_by_id = {q.id: q for q in questions}

    for answer in result.answers:
        if answer.question_id not in questions_by_id:
            raise ValueError(f"Question ID {answer.question_id} not found in state")

        if answer.final_answer:
            questions_by_id[answer.question_id].final_answer = answer.final_answer

    return {"questions": ListQuestions(questions=questions)}
