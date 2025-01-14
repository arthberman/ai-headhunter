from typing import List, Dict
from pydantic import BaseModel, Field


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


class QueryMemory(BaseModel):
    """Tracks what has been tried and what worked/didn't work."""

    failed_attempts: List[QueryAttempt] = Field(
        default_factory=list,
        description="Queries that ended with 0 results after all optimizations",
    )
    successful_attempts: List[QueryAttempt] = Field(
        default_factory=list, description="Queries that ended with 30-1000 results"
    )
    optimization_stats: Dict[str, Dict[str, int]] = Field(
        default_factory=dict,
        description="Statistics about optimization strategy effectiveness",
    )
