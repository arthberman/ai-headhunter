import logging
from typing import Literal

from langgraph.types import Command

from feeder.subgraph.query_optimization.state import QueryOptimizationState

logger = logging.getLogger(__name__)

# Constants for query result bounds
MIN_ACCEPTABLE_RESULTS = 30
MAX_ACCEPTABLE_RESULTS = 1000


def analyze_current_query(
    state: QueryOptimizationState,
) -> Command[
    Literal[
        "optimize_low_results",
        "optimize_high_results",
        "analyze_current_query",
        "__end__",
    ]
]:
    """Check if the current query needs optimization.

    If current query has an acceptable number of results, the graph will move to the next query.
    If all queries have been analyzed, the graph will move to results synthesizer node.
    """
    try:
        # If all queries have been analyzed, go to results synthesizer node
        current_query_index = state.current_query_index
        if current_query_index >= len(state.query_results):
            logger.info(
                "All queries have been analyzed - moving to results synthesizer"
            )
            return Command(
                update={"current_query_index": current_query_index},
                goto="__end__",
            )
        else:
            current_query = state.query_results[current_query_index]

            logger.info(f"Analyzing query {current_query_index + 1}")
            # Get the latest count for the current query
            latest_count = current_query.iterations[-1].count
            if latest_count is None:
                raise ValueError(
                    f"Latest iteration for query {current_query_index} has no count"
                )

            if latest_count < MIN_ACCEPTABLE_RESULTS:
                logger.info(
                    f"Query {current_query_index + 1} has {latest_count} results - go to optimize_low_results"
                )
                return Command(
                    goto="optimize_low_results",
                )
            elif latest_count > MAX_ACCEPTABLE_RESULTS:
                logger.info(
                    f"Query {current_query_index + 1} has {latest_count} results - go to optimize_high_results"
                )
                return Command(
                    goto="optimize_high_results",
                )
            else:
                # If the current query is optimal, move to the next query
                logger.info(
                    f"Query {current_query_index + 1} is optimal - moving to next query"
                )
                current_query.is_optimized = True
                return Command(
                    goto="analyze_current_query",
                    update={
                        "current_query_index": current_query_index + 1,
                        "query_results": state.query_results,
                    },
                )
    except Exception as e:
        logger.error(f"Error validating current query: {e}")
        raise e
