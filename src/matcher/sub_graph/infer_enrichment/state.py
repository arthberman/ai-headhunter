from typing import Annotated, List

from pydantic import BaseModel, Field

from matcher.models.profile import Profile
from matcher.sub_graph.infer_enrichment.models import (
    InferredAttribute,
    reducer_inferred_attributes,
)


class MainInferEnrichmentState(BaseModel):
    """State for the matcher graph."""

    profile: Profile = Field(...)


class OutputInferEnrichmentState(MainInferEnrichmentState):
    """Output state for the enrichment subgraph."""

    inferred_attributes: Annotated[
        List[InferredAttribute], reducer_inferred_attributes
    ] = Field(default_factory=list)
