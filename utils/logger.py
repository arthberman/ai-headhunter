import functools


def log_process(logger):
    def decorator(func):
        @functools.wraps(func)  # This preserves the original function name and metadata
        async def wrapper(*args, **kwargs):
            logger.info(f"Starting {func.__name__}")
            try:
                result = await func(*args, **kwargs)
                logger.info(f"Completed {func.__name__}")
                return result
            except Exception as e:
                logger.error(f"Error in {func.__name__}: {str(e)}", exc_info=True)
                raise

        return wrapper

    return decorator
