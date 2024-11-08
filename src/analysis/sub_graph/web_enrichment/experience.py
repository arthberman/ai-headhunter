from datetime import datetime
from typing import cast

from langchain_community.tools import TavilySearchResults
from langchain_core.runnables import Runnable, RunnableConfig
from langgraph.store.base import BaseStore

from analysis.full.configuration import Configuration
from analysis.models.company import CompanyInfo
from analysis.models.profile import ProfileExperience
from analysis.sub_graph.web_enrichment.state import (
    ExperienceState,
    OutputEnrichmentState,
)
from utils import get_prompt, init_model

tavily_tool = TavilySearchResults(
    max_results=10, include_answer=True, search_depth="advanced"
)


def node_experience_enrichment(
    state: ExperienceState, *, config: RunnableConfig, store: BaseStore
) -> OutputEnrichmentState:
    """Enrich the experience of the candidate."""
    experience: ProfileExperience = state["experience"]

    # If no linkedin_url or invalid format, return empty
    if not experience.linkedin_url or not experience.linkedin_url.startswith(
        "https://www.linkedin.com/company/"
    ):
        return {"experience_enrichment": []}

    # Load configuration from the provided RunnableConfig
    configuration = Configuration.from_runnable_config(config)

    # Access store
    namespace = ("company", "web_enrichment")
    key = experience.linkedin_url.rstrip("/").split("/")[-1].lower().strip()
    company = store.get(namespace, key)

    if company:
        return {"experience_enrichment": [CompanyInfo(**company.value)]}

    # If not in store, perform Tavily search
    tavily_res = tavily_tool.invoke(
        {"query": f"company {experience.company} ({experience.location})"}
    )
    prompt = get_prompt("generate-experience-enrichment")

    # Initialize the chat model with the provided configuration
    raw_model = init_model(configuration.enrichment_model)
    model = raw_model.with_structured_output(CompanyInfo)

    chain = cast(Runnable, prompt | model)
    res = cast(
        CompanyInfo,
        chain.invoke(
            {
                "web_browsing_result": tavily_res,
                "company": experience.company,
                "company_title": experience.title,
                "company_description": experience.description,
                "linkedin_url": experience.linkedin_url,
                "output_schema": CompanyInfo.model_json_schema(),
                "output_language": configuration.output_language,
                "system_time": datetime.now().strftime("%Y-%m-%d (Y-m-d)"),
            }
        ),
    )

    # Add the new company info to the store
    store.put(namespace, key, res)

    return {"experience_enrichment": [res]}
