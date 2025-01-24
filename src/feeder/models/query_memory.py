from typing import List

from pydantic import BaseModel, Field


class OptimizationMetrics(BaseModel):
    """Metrics for a specific optimization strategy."""

    success_count: int = Field(default=0)
    failure_count: int = Field(default=0)
    total_attempts: int = Field(default=0)


class StrategyStats(BaseModel):
    """Statistics for a specific strategy."""

    strategy_name: str = Field(description="Name of the optimization strategy")
    metrics: OptimizationMetrics = Field(default_factory=OptimizationMetrics)


class QueryAttempt(BaseModel):
    """Represents a complete query attempt with all its optimization iterations."""

    query: str = Field(description="The actual query string used")
    optimization_journey: List[str] = Field(
        description="List of optimization strategies attempted"
    )
    results_journey: List[int] = Field(
        description="List of result counts after each optimization"
    )
    final_status: str = Field(
        description="Final status: 'success' (30-1000), 'too_many' (>1000), 'too_few' (<30), 'failed' (0)"
    )

    def __str__(self) -> str:
        """Create a concise string representation of the query attempt."""
        filters = []
        for line in self.query.split("], "):
            if "IN: 'in'" in line and "CURRENT_TITLE" in line:
                titles = line.split("value=[")[1].strip("']").split("', '")
                filters.append(f"titles: {titles}")
            elif "NOT_IN: 'not in'" in line and "CURRENT_TITLE" in line:
                excluded = line.split("value=[")[1].strip("']").split("', '")
                filters.append(f"excluded: {excluded}")
            elif "KEYWORD" in line:
                keywords = line.split("value=[")[1].strip("']").split("', '")
                filters.append(f"keywords: {keywords}")

        return (
            f"Query({', '.join(filters)}) → "
            f"Journey: {list(zip(self.optimization_journey, self.results_journey))} → "
            f"Status: {self.final_status}"
        )


class QueryMemory(BaseModel):
    """Tracks the history and effectiveness of query optimization attempts.

    This class serves as a memory system that:
    1. Records both successful and failed query attempts to learn from past optimizations
    2. Maintains statistics about different optimization strategies' effectiveness
    3. Helps avoid repeating unsuccessful query patterns

    The memory is used to:
    - Inform the LLM about what worked/didn't work in previous attempts
    - Guide strategy selection in subsequent optimization rounds
    - Provide analytics about strategy effectiveness
    """

    failed_attempts: List[QueryAttempt] = Field(
        default_factory=list,
        description="Queries that ended with 0 results after all optimizations. "
        "These attempts help identify patterns to avoid and inform the "
        "first-generation query process to prevent similar failures.",
    )

    successful_attempts: List[QueryAttempt] = Field(
        default_factory=list,
        description="Queries that ended with 30-1000 results. These attempts serve as "
        "positive examples for future query generation and help identify "
        "effective patterns in terms of keyword combinations and job title selections.",
    )

    strategy_statistics: List[StrategyStats] = Field(
        default_factory=list,
        description="Statistics about optimization strategy effectiveness. These stats "
        "inform the strategy selection process by tracking success rates of different "
        "approaches (e.g., removing keywords, adding far keywords, etc.). "
        "Strategies with higher success rates are preferred in future optimizations.",
    )

    def __str__(self) -> str:
        """Create a concise string representation of the memory."""
        parts = []

        # Add failed attempts - helps identify problematic patterns
        if self.failed_attempts:
            parts.append("Failed Attempts:")
            for attempt in self.failed_attempts:
                parts.append(f"  {attempt}")

        # Add successful attempts - serves as reference for effective queries
        if self.successful_attempts:
            parts.append("Successful Attempts:")
            for attempt in self.successful_attempts:
                parts.append(f"  {attempt}")

        # Add strategy statistics - shows effectiveness of different optimization approaches
        if self.strategy_statistics:
            parts.append("Strategy Statistics:")
            for stat in self.strategy_statistics:
                metrics = stat.metrics
                parts.append(
                    f"  {stat.strategy_name}: "
                    f"{metrics.success_count} successes, "
                    f"{metrics.failure_count} failures"
                )

        return "\n".join(parts)

    def get_strategy_stats(self, strategy_name: str) -> OptimizationMetrics:
        """Get or create statistics for a specific strategy.

        Used to track and update the effectiveness of different optimization approaches.
        These statistics help inform future strategy selection by providing success rates.
        """
        for stat in self.strategy_statistics:
            if stat.strategy_name == strategy_name:
                return stat.metrics

        # If strategy not found, create new stats
        new_stats = StrategyStats(strategy_name=strategy_name)
        self.strategy_statistics.append(new_stats)
        return new_stats.metrics

    def update_optimization_stats(self, strategy: str, success: bool) -> None:
        """Update optimization statistics for a given strategy.

        This method maintains a running tally of successes and failures for each strategy,
        which is used to:
        1. Calculate strategy success rates
        2. Inform strategy selection in future optimization attempts
        3. Identify most reliable optimization approaches
        4. Guide the order in which strategies are attempted
        """
        metrics = self.get_strategy_stats(strategy)
        metrics.total_attempts += 1
        if success:
            metrics.success_count += 1
        else:
            metrics.failure_count += 1
