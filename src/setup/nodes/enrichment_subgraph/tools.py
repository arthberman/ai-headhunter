# First we initialize the model we want to use.
from typing import Any, List, Optional, cast

from langchain_community.tools import TavilySearchResults
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field

from setup.configuration import Configuration


class WebResource(BaseModel):
    """Respond to the user with this tool."""

    resources_enriched: List[str] = Field(
        description="List of text summaries related to web search results"
    )


async def search_web(
    query: str, *, config: RunnableConfig
) -> Optional[list[dict[str, Any]]]:
    """Query a search engine.

    This function queries the web to fetch comprehensive, accurate, and trusted results. It's particularly useful
    for answering questions about current events. Provide as much context in the query as needed to ensure high recall.
    """
    configuration = Configuration.from_runnable_config(config)
    wrapped = TavilySearchResults(max_results=configuration.max_search_results)
    result = await wrapped.ainvoke({"query": query})
    return cast(list[dict[str, Any]], result)


def get_tools() -> List[BaseTool]:
    """Get the tools for the enrichment subgraph."""
    tools = [search_web, WebResource]
    return tools
