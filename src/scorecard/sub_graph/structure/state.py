from typing import List, Optional
from pydantic import BaseModel, Field
from scorecard.models.question import Question
from scorecard.models.scorecard import Scorecard
from scorecard.sub_graph.structure.models import StructureAction


class StructureGraphState(BaseModel):
    raw_job_posting: str = Field(
        ..., description="Raw job posting with all the context provided by the user"
    )
    global_context: Optional[List[str]] = Field(
        description="List of context elements from the web search"
    )
    questions: Optional[List[Question]] = Field(
        description="List of questions for human in the loop"
    )
    scorecard: Optional[Scorecard] = Field(
        None, description="Scorecard with all the criteria and questions"
    )
    structure_actions: Optional[List[StructureAction]] = Field(
        None, description="List of actions to be taken to structure the scorecard"
    )
    is_structure_valid: Optional[bool] = Field(
        None, description="Whether the scorecard is valid"
    )
    recursion_count: int = Field(
        0, description="Number of times the judge has been called"
    )
