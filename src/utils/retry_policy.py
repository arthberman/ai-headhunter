from langgraph.pregel import RetryPolicy


def get_retry_policy() -> RetryPolicy:
    """Get the retry policy."""
    return RetryPolicy(
        initial_interval=1.0,
        backoff_factor=2.0,
        max_attempts=3,
        jitter=True,
    )
