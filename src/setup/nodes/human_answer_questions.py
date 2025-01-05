import uuid
from typing import List

from langgraph.types import interrupt
from pydantic import BaseModel, Field

from setup.state import (
    BaseResource,
    QuestionResource,
    ResourceOrigin,
    ResourceType,
    ScorecardGraphState,
)


class Answer(BaseModel):
    """An answer to a question."""

    id: uuid.UUID = Field(..., description="The ID of the question")
    final_answer: str = Field(..., description="The final answer to the question")


class Response(BaseModel):
    """Expected response structure from human answer questions interrupt."""

    final_answers: List[Answer] = Field(
        ..., description="The final answers to the questions"
    )


async def node_human_answer_questions(
    state: ScorecardGraphState,
) -> ScorecardGraphState:
    """Human answer questions."""
    # Store the questions first to maintain stable references
    questions = state.generated_questions.questions

    result = Response.model_validate(
        interrupt(
            {
                "task": "answer_questions",
                "questions": questions,
            }
        )
    )

    # Create a set of question IDs for efficient lookup
    question_ids = {q.id for q in questions}

    # Check if ID returned corresponds to a question in the state
    for answer in result.final_answers:
        if answer.id not in question_ids:
            raise ValueError(f"Question ID {answer.id} not found in state")

    # BaseResource for each answer with QuestionContext type-specific fields
    for answer in result.final_answers:
        if not answer.final_answer:
            continue

        state.resources.append(
            BaseResource(
                source=ResourceOrigin.HUMAN,
                content_type=ResourceType.QUESTION,
                content=answer.final_answer,
                type_specific=QuestionResource(question_id=answer.id),
            )
        )

    return {"resources": state.resources}
