from typing import List, Optional
from pydantic import BaseModel, Field
from scorecard.models.question import Question
from scorecard.models.scorecard import Scorecard
from scorecard.state import ScorecardGraphState
from scorecard.sub_graph.structure.models import StructureAction


class StructureGraphState(ScorecardGraphState):
    structure_actions: Optional[List[StructureAction]] = Field(
        None, description="List of actions to be taken to structure the scorecard"
    )
    is_structure_valid: Optional[bool] = Field(
        None, description="Whether the scorecard is valid"
    )
    recursion_count: int = Field(
        0, description="Number of times the judge has been called"
    )
