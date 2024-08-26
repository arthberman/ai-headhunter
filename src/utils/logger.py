import logging
import math
import time
from typing import Callable

class CustomFormatter(logging.Formatter):
    def format(self, record):
        # Format timestamp
        timestamp = time.strftime("%m/%d/%Y, %I:%M:%S %p")

        # Construct the log message
        log_msg = f"[repio-intelligence] {record.process:<5} - {timestamp}     {record.levelname:<8} [{record.name}] {record.getMessage()}"

        # Apply color
        green = "\033[32m"
        white = "\033[37m"
        yellow = "\033[33m"
        reset = "\033[0m"

        colored_msg = (
            f"{green}[repio] {record.process:<5} -{reset}"
            f"{white} {timestamp} {reset}    "
            f"{green}{record.levelname:<8}{reset} "
            f"{yellow}[{record.name}]{reset} "
            f"{green}{record.getMessage()}{reset}"
        )

        if "+ms" in record.getMessage():
            colored_msg += f" {yellow}{record.getMessage().split('+')[-1]}{reset}"

        return colored_msg

def setup_logger():
    handler = logging.StreamHandler()
    handler.setFormatter(CustomFormatter())

    logger = logging.getLogger("repio")
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

    # Set HTTPX logger to ERROR level
    httpx_logger = logging.getLogger("httpx")
    httpx_logger.setLevel(logging.ERROR)

    return logger

def log_process(logger: logging.Logger) -> Callable:
    """Decorator to log the start and end of a process"""

    def decorator(func):
        async def wrapper(*args, **kwargs):
            try:
                process_name = func.__name__
                job = args[0] if args else None
                trackId = f"analysis id {job.data['analysisId']}" if job.data.get("analysisId") else f"job id {job.id}"

                logger.info(f"Starting process: {process_name} {trackId}")
                start_time = time.time()
                result = await func(*args, **kwargs)
                end_time = time.time()

                duration_seconds = end_time - start_time
                minutes = math.floor(duration_seconds / 60)
                seconds = math.floor(duration_seconds % 60)

                if minutes > 0:
                    duration_formatted = f"{minutes}m{seconds}s"
                else:
                    duration_formatted = f"{seconds}s"

                logger.info(
                    f"Finished process: {process_name} {trackId} +{duration_formatted}"
                )
                return result
            except Exception as e:
                logger.error(f"Error with log_process: {str(e)}", exc_info=True)
                raise ValueError(f"Error with log_process: {str(e)}") from e

        return wrapper

    return decorator
