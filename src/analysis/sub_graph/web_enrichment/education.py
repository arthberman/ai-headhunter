from typing import cast

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

    # Access store
    namespace = ("school", "enrichment")
    key = education.linkedin_url.rstrip("/").split("/")[-1].lower().strip()
    school = await store.aget(namespace, key)

    if school:
        return {"education_enrichment": [cast(SchoolInfo, school.value)]}

    # If not in store, perform Tavily search
    tavily_res = await tavily_tool.ainvoke(
        {"query": f"school {education.school} ({education.linkedin_url})"}
    )

    # Call the memory_graph
    memory_client = get_client()
    await memory_client.runs.wait(
        thread_id=None,
        assistant_id=configuration.mem_assistant_id,
        input={
            "namespace": namespace,
            "key": key,
            "function_name": "School",
            "information": f"""<web_search>
                {tavily_res}
                </web_search>
                
                <candidate_profile>
                School: {education.school}
                Description: {education.description}
                </candidate_profile>""",
        },
    )

    # Add the new school info to the store
    school = await store.aget(namespace, key)
    if not school:
        raise ValueError("School not found in the store.")

    return {"education_enrichment": [cast(SchoolInfo, school.value)]}
