from typing import List, Literal, Optional

from pydantic import BaseModel, Field

from feeder.models.people_search_filter import PeopleSearchFilter


class OptimizationStrategy(BaseModel):
    """Represents an optimization strategy with its status."""

    strategy_type: Literal[
        "remove_quotes",
        "add_far_keywords",
        "remove_keywords",
        "remove_seniority",
        "broaden_titles",  # todo: introduce a unique_titles list coming and implement the method
    ]
    attempted: bool = False
    succeeded: bool = False


class QueryIteration(BaseModel):
    """Represents one iteration of a query with its results."""

    filters: PeopleSearchFilter
    count: Optional[int] = Field(None)
    # unique_titles: Optional[List[str]] = None
    optimization_reason: Optional[str] = Field(None)
    strategy_used: Optional[str] = Field(None)


class FilterQuery(BaseModel):
    """Tracks all iterations of a specific query."""

    original_filters: PeopleSearchFilter
    iterations: List[QueryIteration] = Field(default_factory=list)
    is_optimized: bool = Field(default=False)
    optimization_attempt: int = Field(default=0)
    optimization_strategies: List[OptimizationStrategy] = Field(default_factory=list)
    child_queries: List["FilterQuery"] = Field(default_factory=list)

    def split_query(self, new_filters_list: List[PeopleSearchFilter], reason: str):
        """Create child queries when splitting a query."""
        for filters in new_filters_list:
            child_query = FilterQuery(
                original_filters=filters,
                iterations=[
                    QueryIteration(filters=filters, count=0, optimization_reason=reason)
                ],
            )
            self.child_queries.append(child_query)

    def __init__(self, **data):
        """Initialize the FilterQuery with default optimization strategies."""
        super().__init__(**data)
        if not self.optimization_strategies:
            print("\n" + "=" * 50)
            print("Initializing optimization strategies")
            print("=" * 50)

            # Base strategies list
            strategies = [OptimizationStrategy(strategy_type="remove_quotes")]
            print("✓ Added remove_quotes strategy")

            # Add far_keywords strategy as second if we have far keywords
            if (
                "keywords_classified" in data
                and data["keywords_classified"]
                and data["keywords_classified"].get("far")
            ):
                strategies.append(
                    OptimizationStrategy(strategy_type="add_far_keywords")
                )
                print("✓ Added add_far_keywords strategy (FAR keywords found)")
                print(f"FAR keywords: {data['keywords_classified'].get('far')}")
            else:
                print("✗ Skipped add_far_keywords strategy (no FAR keywords found)")

            # Add remaining strategies
            remaining = [
                "remove_keywords",
                "remove_seniority",
                "broaden_titles",
            ]
            for strategy in remaining:
                strategies.append(OptimizationStrategy(strategy_type=strategy))
                print(f"✓ Added {strategy} strategy")

            print("\nFinal strategy order:")
            for i, strategy in enumerate(strategies, 1):
                print(f"{i}. {strategy.strategy_type}")
            print("=" * 50 + "\n")

            self.optimization_strategies = strategies

    @property
    def latest_filters(self) -> PeopleSearchFilter:
        """Get the latest filters from the iterations."""
        if self.iterations:
            return self.iterations[-1].filters
        return self.original_filters

    def get_next_strategy(self) -> Optional[OptimizationStrategy]:
        """Get next untried optimization strategy."""
        for strategy in self.optimization_strategies:
            if not strategy.attempted:
                return strategy
        return None

    def add_iteration(
        self,
        filters: PeopleSearchFilter,
        profile_count: int,
        optimization_reason: Optional[str] = None,
        strategy_used: Optional[str] = None,
    ):
        """Add a new iteration to the query."""
        self.iterations.append(
            QueryIteration(
                filters=filters,
                count=profile_count,
                optimization_reason=optimization_reason,
                strategy_used=strategy_used,
            )
        )

    @property
    def is_complete(self) -> bool:
        """Check if query is complete and shouldn't be optimized further."""
        # Query split into children
        if self.child_queries:
            return True

        # Latest results are optimal
        if self.iterations and 30 <= self.iterations[-1].count <= 1000:
            return True

        # No more optimization strategies available
        if not self.get_next_strategy():
            return True

        # Max iterations reached for this query
        if len(self.iterations) >= 4:  # You can adjust this number
            return True

        return False

    @property
    def optimization_status(self) -> str:
        """Get the current status of the query optimization."""
        if not self.iterations:
            return "pending"

        latest_count = self.iterations[-1].count

        if self.child_queries:
            return "split"
        elif 30 <= latest_count <= 1000:
            return "optimal"
        elif latest_count > 1000:
            return "too_high"
        elif latest_count < 30:
            return "too_low"
        else:
            return "in_progress"


class FilterQueryList(BaseModel):
    """Collection of queries with their metrics."""

    results: List[FilterQuery] = Field(default_factory=list)

    def add_result(self, query: PeopleSearchFilter, profile_count: int):
        """Add a new query result."""
        self.results.append(FilterQuery(query=query, count=profile_count))
