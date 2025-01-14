import os
from functools import lru_cache

from langchain import hub
from langchain_core.prompts import ChatPromptTemplate


@lru_cache(maxsize=32)  # Cache up to 128 most recent prompts
def get_prompt(prompt_name: str) -> ChatPromptTemplate:
    """Get a prompt from LangChain Hub with caching."""
    # Modify prompt name if in production
    if os.getenv("ENV") == "production":
        prompt_name = f"{prompt_name}:production"

    # Pull from hub
    try:
        prompt = hub.pull(prompt_name)
        return prompt
    except Exception as e:
        raise Exception(f"Error fetching prompt from LangChain Hub: {str(e)}")
