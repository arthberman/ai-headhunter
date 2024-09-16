# First we initialize the model we want to use.
from typing import List

from langchain_community.tools import TavilySearchResults
from pydantic import BaseModel, Field
from langchain_core.tools import BaseTool


class WebContext(BaseModel):
    """Respond to the user with this"""

    web_context: List[str] = Field(
        description="List of context elements (results from the web search)"
    )


def get_tools() -> List[BaseTool]:
    tavily_tool = TavilySearchResults(
        max_results=5,
        include_answer=True,
    )

    tools = [tavily_tool, WebContext]
    return tools
