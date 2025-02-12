import operator
from typing import Annotated, List, Optional

from langgraph.store.base import Op
from pydantic import BaseModel, Field

from matcher.memory.models.company import CompanyInfo
from matcher.memory.models.school import SchoolInfo
from matcher.models.profile import Profile
from matcher.models.scored_criterion import reducer_scored_criterion
from matcher.sub_graph.criterion_matcher.models import ScoredCriterion
from matcher.sub_graph.decision.models import (
    Conclusion,
    Decision,
    DecisionType,
    reducer_decisions,
)
from matcher.sub_graph.infer_enrichment.models import (
    InferredAttribute,
    InferredAttributeType,
    reducer_inferred_attributes,
)
from setup.models.scorecard import Scorecard
from utils import reducer_list


class InputGraphState(BaseModel):
    """State of the input graph."""

    profile: Profile = Field(...)
    scorecard: Scorecard = Field(...)
    job_synthesis: str = Field(...)


class OutputGraphState(BaseModel):
    """State of the output graph."""

    scored_criterion: Annotated[List[ScoredCriterion], reducer_scored_criterion] = (
        Field(default_factory=list)
    )
    inferred_attributes: Annotated[
        List[InferredAttribute], reducer_inferred_attributes
    ] = Field(default_factory=list)
    decisions: Annotated[List[Decision], reducer_decisions] = Field(
        default_factory=list
    )
    conclusion: Optional[Conclusion] = Field(default=None)

    def get_decision(self, decision_type: DecisionType) -> Optional[Decision]:
        """Get a decision by its type."""
        for decision in self.decisions:
            if decision.type == decision_type:
                return decision
        return None

    def get_inferred_attribute(
        self, attribute_type: InferredAttributeType
    ) -> Optional[InferredAttribute]:
        """Get an inferred attribute by its type."""
        for attribute in self.inferred_attributes:
            if attribute.type == attribute_type:
                return attribute
        return None


class MainGraphState(InputGraphState, OutputGraphState):
    """State of the main graph."""

    education_enrichment: Annotated[List[SchoolInfo], operator.add]
    experience_enrichment: Annotated[List[CompanyInfo], operator.add]

    batch_store_ops: Annotated[List[Op], reducer_list] = Field(default_factory=list)
