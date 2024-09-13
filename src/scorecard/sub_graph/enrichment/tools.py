# First we initialize the model we want to use.
from typing import List

from langchain_community.tools import TavilySearchResults
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.tools import BaseTool


class GlobalContext(BaseModel):
    """Respond to the user with this"""

    global_context: List[str] = Field(
        description="List of context elements (results from the web search)"
    )


def get_tools() -> List[BaseTool]:
    tavily_tool = TavilySearchResults(
        max_results=5,
        include_answer=True,
    )

    tools = [tavily_tool, GlobalContext]
    return tools
