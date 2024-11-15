from typing import Optional, cast

from langchain_community.tools import TavilySearchResults
from langchain_core.runnables import RunnableConfig
from langgraph.store.base import BaseStore, PutOp

from analysis.memory.handle_patch_memory import handle_patch_memory
from analysis.memory.models.company import CompanyInfo
from analysis.models.profile import ProfileExperience
from analysis.sub_graph.web_enrichment.state import (
    ExperienceState,
    MainEnrichmentState,
)

tavily_tool = TavilySearchResults(
    max_results=10, include_answer=True, search_depth="advanced"
)


def format_information(
    experience: ProfileExperience,
    tavily_res: Optional[str] = None,
) -> str:
    """Format input for memory client with optional Tavily search results."""
    information = f"""
        <candidate_profile>
        Company: {experience.company}
        Location: {experience.location}"""

    # Add title and description only if description is rich
    if len(experience.description) >= 100:
        information += f"""
        Title: {experience.title}
        Description: {experience.description}"""

    information += "\n        </candidate_profile>"

    # Add Tavily results if provided
    if tavily_res:
        information = f"""
            <web_search>
            {tavily_res}
            </web_search>
            {information}"""

    return information


def node_experience_enrichment(
    state: ExperienceState, *, config: RunnableConfig, store: BaseStore
) -> MainEnrichmentState:
    """Enrich the experience of the candidate."""
    experience = cast(ProfileExperience, state["experience"])

    # If no linkedin_url or invalid format, return empty
    if not experience.linkedin_url or not experience.linkedin_url.startswith(
        "https://www.linkedin.com/company/"
    ):
        return {"experience_enrichment": []}

    # Access store
    namespace = ("company", "enrichment")
    key = experience.linkedin_url.rstrip("/").split("/")[-1].lower().strip()
    company = store.get(namespace, key)

    if company:
        company_info = cast(CompanyInfo, company.value)
        if len(experience.description) < 100:
            return {"experience_enrichment": [company_info]}

        # If the description is rich, we can enrich the company info
        op = cast(
            PutOp,
            handle_patch_memory(
                namespace,
                key,
                format_information(experience),
                existing_item=company,
                prompt="memory-company",
                schema_model=CompanyInfo,
                config=config,
            ),
        )
        return {
            "experience_enrichment": [cast(CompanyInfo, op.value)],
            "batch_store_ops": [op],
        }
    else:
        # If not in store or cast failed, perform Tavily search
        tavily_res = tavily_tool.invoke(
            {"query": f"company {experience.company} ({experience.location})"}
        )

        op = cast(
            PutOp,
            handle_patch_memory(
                namespace,
                key,
                format_information(experience, tavily_res),
                existing_item=company,
                prompt="memory-company",
                schema_model=CompanyInfo,
                config=config,
            ),
        )

        return {
            "experience_enrichment": [cast(CompanyInfo, op.value)],
            "batch_store_ops": [op],
        }
