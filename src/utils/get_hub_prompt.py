import os
from typing import Any, Dict

from langchain import hub

# Cache dictionary to store prompts
_prompt_cache: Dict[str, Any] = {}


def get_hub_prompt(prompt_name: str) -> Any:
    """Get a prompt from LangChain Hub with caching."""
    # Modify prompt name if in production
    if os.getenv("ENV") == "production":
        prompt_name = f"{prompt_name}:production"

    # Check if prompt is already in cache
    if prompt_name in _prompt_cache:
        return _prompt_cache[prompt_name]

    # If not in cache, pull from hub and store in cache
    prompt = hub.pull(prompt_name)
    _prompt_cache[prompt_name] = prompt

    return prompt
