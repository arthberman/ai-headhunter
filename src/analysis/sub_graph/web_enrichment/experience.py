from typing import cast

from langchain_community.tools import TavilySearchResults
from langchain_core.runnables import RunnableConfig
from langgraph.store.base import BaseStore
from langgraph_sdk import get_client

from analysis.full.configuration import Configuration
from analysis.models.profile import ProfileExperience
from analysis.sub_graph.web_enrichment.state import (
    ExperienceState,
    OutputEnrichmentState,
)
from memory_graph.models.company import CompanyInfo

tavily_tool = TavilySearchResults(
    max_results=10, include_answer=True, search_depth="advanced"
)


async def node_experience_enrichment(
    state: ExperienceState, *, config: RunnableConfig, store: BaseStore
) -> OutputEnrichmentState:
    """Enrich the experience of the candidate."""
    experience = cast(ProfileExperience, state["experience"])

    # If no linkedin_url or invalid format, return empty
    if not experience.linkedin_url or not experience.linkedin_url.startswith(
        "https://www.linkedin.com/company/"
    ):
        return {"experience_enrichment": []}

    # Load configuration from the provided RunnableConfig
    configuration = Configuration.from_runnable_config(config)

    # Access store
    namespace = ("company", "enrichment")
    key = experience.linkedin_url.rstrip("/").split("/")[-1].lower().strip()
    company = await store.aget(namespace, key)

    if company:
        return {"experience_enrichment": [cast(CompanyInfo, company.value)]}

    # If not in store, perform Tavily search
    tavily_res = await tavily_tool.ainvoke(
        {"query": f"company {experience.company} ({experience.location})"}
    )

    # Call the memory_graph
    memory_client = get_client()
    await memory_client.runs.wait(
        thread_id=None,
        assistant_id=configuration.mem_assistant_id,
        input={
            "namespace": namespace,
            "key": key,
            "function_name": "Company",
            "information": f"""<web_search>
                {tavily_res}
                </web_search>
                
                <candidate_profile>
                Company: {experience.company}
                Title: {experience.title}
                Description: {experience.description}
                </candidate_profile>""",
        },
    )

    # Add the new company info to the store
    company = await store.aget(namespace, key)
    if not company:
        raise ValueError("Company not found in the store.")

    return {"experience_enrichment": [cast(CompanyInfo, company.value)]}
