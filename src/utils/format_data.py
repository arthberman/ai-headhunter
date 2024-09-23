from datetime import datetime
from enum import Enum


def format_data(data):
    if isinstance(data, dict):
        return {k: format_data(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [format_data(item) for item in data]
    elif isinstance(data, datetime):
        return data.strftime("%Y-%m-%d")
    elif isinstance(data, Enum):
        return data.value
    elif hasattr(data, "__dict__"):
        return format_data(data.__dict__)
    else:
        return data
