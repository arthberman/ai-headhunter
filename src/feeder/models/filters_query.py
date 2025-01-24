import uuid
from logging import getLogger
from typing import List, Literal, Optional

from pydantic import BaseModel, Field, field_validator

from feeder.models.people_search_filter import PeopleSearchFilter, TextFilter

logger = getLogger(__name__)


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

    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    filters: List[TextFilter] = Field(
        ..., description="List of filters to apply to the search."
    )
    count: Optional[int] = Field(None)

    optimization_reason: Optional[str] = Field(None)
    strategy_used: Optional[str] = Field(None)

    @field_validator("filters")
    def validate_filters(cls, v: List[TextFilter]) -> List[TextFilter]:
        """Validate the filters list."""
        if not v:
            raise ValueError("Filters list cannot be empty")
        return v


class FilterQuery(BaseModel):
    """Tracks all iterations of a specific query."""

    original_filters: List[TextFilter] = Field(
        ..., description="List of filters to apply to the search."
    )
    iterations: List[QueryIteration] = Field(default_factory=list)
    is_optimized: bool = Field(default=False)
    optimization_attempt: int = Field(default=0)
    optimization_strategies: List[OptimizationStrategy] = Field(default_factory=list)

    def split_query(
        self, new_filters_list: List[List[TextFilter]], reason: str
    ) -> List["FilterQuery"]:
        """Create new queries when splitting a query."""
        new_queries = []
        for filters in new_filters_list:
            new_query = FilterQuery(
                original_filters=filters,
                iterations=[
                    QueryIteration(
                        filters=filters,
                        count=None,
                        optimization_reason=reason,
                    )
                ],
            )
            new_queries.append(new_query)
        return new_queries

    def __init__(self, **data):
        """Initialize the FilterQuery with default optimization strategies."""
        super().__init__(**data)
        if not self.optimization_strategies:
            logger.info("\n" + "=" * 50)
            logger.info("Initializing optimization strategies")
            logger.info("=" * 50)

            # Base strategies list
            strategies = [OptimizationStrategy(strategy_type="remove_quotes")]
            logger.info("✓ Added remove_quotes strategy")

            # Add far_keywords strategy as second if we have far keywords
            if (
                "keywords_classified" in data
                and data["keywords_classified"]
                and data["keywords_classified"].far
                and len(data["keywords_classified"].far) > 0
            ):
                strategies.append(
                    OptimizationStrategy(strategy_type="add_far_keywords")
                )
                logger.info("✓ Added add_far_keywords strategy (FAR keywords found)")
                logger.info(f"FAR keywords: {data['keywords_classified'].far}")
            else:
                logger.info(
                    "✗ Skipped add_far_keywords strategy (no FAR keywords found)"
                )

            # Add remaining strategies
            remaining = [
                "remove_keywords",
                "remove_seniority",
                "broaden_titles",
            ]
            for strategy in remaining:
                strategies.append(OptimizationStrategy(strategy_type=strategy))
                logger.info(f"✓ Added {strategy} strategy")

            logger.info("\nFinal strategy order:")
            for i, strategy in enumerate(strategies, 1):
                logger.info(f"{i}. {strategy.strategy_type}")
            logger.info("=" * 50 + "\n")

            self.optimization_strategies = strategies

    @property
    def latest_filters(self) -> List[TextFilter]:
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
        filters: List[TextFilter],
        profile_count: Optional[int],
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
    def optimization_status(
        self,
    ) -> Literal["pending", "optimal", "too_high", "too_low", "in_progress"]:
        """Get the current status of the query optimization."""
        if not self.iterations:
            return "pending"

        latest_count = self.iterations[-1].count
        if latest_count is None:
            return "in_progress"

        if 30 <= latest_count <= 1000:
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

    def add_result(self, filters: List[TextFilter], profile_count: int):
        """Add a new query result."""
        self.results.append(
            FilterQuery(
                original_filters=filters,
                iterations=[
                    QueryIteration(
                        filters=PeopleSearchFilter(filters=filters), count=profile_count
                    )
                ],
            )
        )
