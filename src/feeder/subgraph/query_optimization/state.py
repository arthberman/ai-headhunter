from typing import List, Optional

from pydantic import BaseModel, Field

from feeder.models.filters_query import FilterQuery
from src.feeder.models.keywords_ranking import KeywordsRankings


class QueryOptimizationInputState(BaseModel):
    """Input state for query optimization subgraph.

    This state represents the initial configuration for query optimization,
    containing the queries to be optimized and tracking the optimization progress.
    """

    query_results: List[FilterQuery] = Field(
        default_factory=list,
        description="List of query variations to try. Each query is progressively optimized "
        "based on search results. If a query returns too many/few results, it will be "
        "modified and added back to this list for another attempt.",
    )

    current_query_index: Optional[int] = Field(
        default=0,
        description="Tracks which query from query_results is currently being optimized. "
        "This allows the optimization process to iterate through multiple query variations "
        "while maintaining state between optimization attempts.",
    )

    keywords_classified: Optional[KeywordsRankings] = Field(
        None,
        description="Ranked keywords used to optimize queries. Keywords are ranked by "
        "specificity/importance, allowing the optimizer to strategically add/remove "
        "keywords to achieve the target number of results.",
    )


class QueryOptimizationOutputState(BaseModel):
    """Output state for query optimization subgraph.

    Contains the final optimized queries that produced acceptable results
    (typically 30-1000 matching profiles).
    """

    query_results: List[FilterQuery] = Field(
        default_factory=list,
        description="List of successfully optimized queries that produced an acceptable "
        "number of results. These queries are ready to be executed for final profile gathering.",
    )


class QueryOptimizationState(QueryOptimizationInputState):
    """State for query optimization subgraph.

    Extends the input state with optimization control parameters.
    """

    max_iterations: int = 4  # Maximum number of optimization attempts per query: controls how many times a single query can be optimized before giving up.
