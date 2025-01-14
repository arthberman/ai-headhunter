from typing import Optional

from pydantic import BaseModel, Field

from feeder.models.filters_query import FilterQueryList


class QueryOptimizationInputState(BaseModel):
    """Input state for query optimization subgraph."""

    query_results: FilterQueryList = Field(None)
    current_query_index: Optional[int] = Field(default=0)
    keywords_classified: Optional[dict] = Field(None)


class QueryOptimizationOutputState(BaseModel):
    """Output state for query optimization subgraph."""

    query_results: FilterQueryList


class QueryOptimizationState(QueryOptimizationInputState):
    """State for query optimization subgraph."""

    max_iterations: int = 4
