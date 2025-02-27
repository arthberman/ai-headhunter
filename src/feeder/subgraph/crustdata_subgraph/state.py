from typing import Optional

from pydantic import BaseModel, Field

from feeder.models.filters_query import FilterQuery


class CrustdataSubgraphState(BaseModel):
    """State model for the CrustData subgraph."""

    query_results: Optional[list[FilterQuery]] = Field(
        description="Query results for crustdata API", default_factory=list
    )
