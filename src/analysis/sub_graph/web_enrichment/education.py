from typing import Any, Dict, Optional, Tuple, cast

from langchain_community.tools import TavilySearchResults
from langchain_core.runnables import RunnableConfig
from langgraph.store.base import BaseStore
from langgraph_sdk import get_client

from analysis.full.configuration import Configuration
from analysis.models.profile import ProfileEducation
from analysis.sub_graph.web_enrichment.state import (
    EducationState,
    OutputEnrichmentState,
)
from memory_graph.models import SchoolInfo

tavily_tool = TavilySearchResults(
    max_results=10, include_answer=True, search_depth="advanced"
)


def format_input(
    namespace: Tuple[str, str],
    key: str,
    education: ProfileEducation,
    tavily_res: Optional[str] = None,
) -> Dict[str, Any]:
    """Format input for memory client with optional Tavily search results."""
    information = f"""
        <candidate_profile>
        School: {education.school}"""

    # Add description only if rich
    if len(education.description) >= 100:
        information += f"""
        Description: {education.description}"""

    information += "\n        </candidate_profile>"

    # Add Tavily results if provided
    if tavily_res:
        information = f"""
            <web_search>
            {tavily_res}
            </web_search>
            {information}"""

    return {
        "namespace": namespace,
        "key": key,
        "function_name": "SchoolInfo",
        "information": information,
    }


async def node_education_enrichment(
    state: EducationState, *, config: RunnableConfig, store: BaseStore
) -> OutputEnrichmentState:
    """Enrich the education of the candidate."""
    education = cast(ProfileEducation, state["education"])

    # If no linkedin_url or invalid format, return empty
    if not education.linkedin_url or not education.linkedin_url.startswith(
        "https://www.linkedin.com/school/"
    ):
        return {"education_enrichment": []}

    # Load configuration from the provided RunnableConfig
    configuration = Configuration.from_runnable_config(config)

    # Get the memory client
    memory_client = get_client()

    # Access store
    namespace = ("school", "enrichment")
    key = education.linkedin_url.rstrip("/").split("/")[-1].lower().strip()
    school = await store.aget(namespace, key)

    if school:
        school_info = cast(SchoolInfo, school.value)
        if len(education.description) < 100:
            return {"education_enrichment": [school_info]}

        # If the description is rich, we can enrich the school info
        await memory_client.runs.create(
            thread_id=None,
            assistant_id=configuration.mem_assistant_id,
            input=format_input(namespace, key, education),
        )
        return {"education_enrichment": [school_info]}
    else:
        # If not in store or cast failed, perform Tavily search
        tavily_res = await tavily_tool.ainvoke(
            {"query": f"school {education.school} ({education.linkedin_url})"}
        )

        # Call the memory_graph
        await memory_client.runs.wait(
            thread_id=None,
            assistant_id=configuration.mem_assistant_id,
            input=format_input(namespace, key, education, tavily_res),
        )

        # Add the new school info to the store
        school = await store.aget(namespace, key)
        if not school:
            raise ValueError("School not found in the store.")

        return {"education_enrichment": [cast(SchoolInfo, school.value)]}
