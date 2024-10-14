import operator
from typing import Annotated, List, Optional

from pydantic import Field

from scorecard.full.state import ScorecardGraphState
from scorecard.nodes.structure_subgraph.models import StructureAction


class StructureGraphState(ScorecardGraphState):
    """State for the structure graph."""

    precedent_actions: Annotated[List[StructureAction], operator.add] = Field(
        [], description="The last action taken to structure the scorecard"
    )
    next_actions: Optional[List[StructureAction]] = Field(
        [], description="List of actions to be taken to structure the scorecard"
    )
    is_structure_valid: Optional[bool] = Field(
        None, description="Whether the scorecard is valid"
    )
    recursion_count: int = Field(
        0, description="Number of times the judge has been called"
    )
