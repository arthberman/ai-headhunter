import operator
from typing import Annotated, List, Optional

from langgraph.store.base import Op
from pydantic import BaseModel, Field

from matcher.memory.models.company import CompanyInfo
from matcher.memory.models.school import SchoolInfo
from matcher.models.language import LanguageProficiency
from matcher.models.profile import Profile
from matcher.models.synthesis import (
    LocationSynthesis,
)
from matcher.sub_graph.criterion_matcher.models import ScoredCriterion
from matcher.sub_graph.decision.models import (
    ConclusionOverall,
    HierarchyMove,
    IntentToMove,
    OpenessToWork,
    RedflagStability,
)
from setup.models.scorecard import Scorecard
from utils import reducer_list


def reducer_scored_criterion(
    existing: List[ScoredCriterion], new: List[ScoredCriterion]
) -> List[ScoredCriterion]:
    """Reducer that replaces existing criteria with new ones if IDs match."""
    # Create a dictionary of existing criteria, excluding ones that will be updated
    existing_dict = {
        criterion.id: criterion
        for criterion in existing
        if criterion.id not in {new_criterion.id for new_criterion in new}
    }

    # Add all new criteria
    for criterion in new:
        existing_dict[criterion.id] = criterion

    return list(existing_dict.values())


class InputGraphState(BaseModel):
    """State of the input graph."""

    profile: Profile = Field(...)
    scorecard: Scorecard = Field(...)
    job_synthesis: str = Field(...)


class MainGraphState(InputGraphState):
    """State of the main graph."""

    education_enrichment: Annotated[List[SchoolInfo], operator.add]
    experience_enrichment: Annotated[List[CompanyInfo], operator.add]

    batch_store_ops: Annotated[List[Op], reducer_list] = Field(default_factory=list)

    inferred_languages: Optional[List[LanguageProficiency]] = Field(default=None)
    inferred_industry_sector: Optional[str] = Field(default=None)
    inferred_culture: Optional[str] = Field(default=None)
    inferred_role_trajectory: Optional[str] = Field(default=None)

    scored_criterion: Annotated[List[ScoredCriterion], reducer_scored_criterion] = (
        Field(default_factory=list)
    )

    synthesis_location: Optional[LocationSynthesis] = Field(default=None)

    conclusion_overall: Optional[ConclusionOverall] = Field(default=None)
    hierarchy_move: Optional[HierarchyMove] = Field(default=None)
    openess_to_work: Optional[OpenessToWork] = Field(default=None)
    intent_to_move: Optional[IntentToMove] = Field(default=None)
    redflag_stability: Optional[RedflagStability] = Field(default=None)
