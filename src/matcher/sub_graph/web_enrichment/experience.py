from typing import Optional, cast

from langchain_community.tools import TavilySearchResults
from langchain_core.runnables import RunnableConfig
from langgraph.store.base import BaseStore, PutOp
from pydantic import ValidationError

from matcher.memory.handle_patch_memory import handle_patch_memory
from matcher.memory.models.company import CompanyInfo
from matcher.models.profile import ProfileExperience
from matcher.sub_graph.web_enrichment.state import (
    ExperienceState,
    MainEnrichmentState,
)

tavily_tool = TavilySearchResults(
    max_results=10, include_answer=True, search_depth="advanced"
)


def format_information(
    experience: ProfileExperience,
    tavily_res: Optional[str] = None,
    old_value: Optional[dict] = None,
) -> str:
    """Format input for memory client with optional Tavily search results and old value."""
    information = f"""
        ***candidate_profile***
        Company: {experience.company}
        Location: {experience.location}"""

    # Add title and description only if description exists and is rich
    description = experience.description or ""  # Handle None case
    if len(description) >= 100:
        information += f"""
        Position Title: {experience.title}
        Position Description: {description}"""
    else:
        information += """
        Position Title: Not provided
        Position Description: Not provided"""

    information += "\n        ***candidate_profile***"

    # Add old value if provided
    if old_value:
        information += f"""
            ***old_value***
            {old_value}
            ***old_value***"""

    # Add Tavily results if provided
    if tavily_res:
        information = f"""
            ***web_search***
            {tavily_res}
            ***web_search***
            {information}"""

    return information


def node_experience_enrichment(
    state: ExperienceState, *, config: RunnableConfig, store: BaseStore
) -> MainEnrichmentState:
    """Enrich the experience of the candidate."""
    experience = cast(ProfileExperience, state["experience"])

    # If no linkedin_id, return empty
    if not experience.linkedin_id:
        return {"experience_enrichment": []}

    # Access store
    namespace = ("company", "enrichment")
    key = experience.linkedin_id.lower().strip()
    company = store.get(namespace, key)

    if company:
        try:
            # Try to validate against current schema
            company_info = CompanyInfo.model_validate(company.value)

            if len(experience.description) < 100:
                return {"experience_enrichment": [company_info]}

            # Update with rich description
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
        except ValidationError:
            # Schema mismatch - treat as if not in store and reprocess
            tavily_res = tavily_tool.invoke(
                {"query": f"company {experience.company} ({experience.location})"}
            )

            # Create new entry with current schema
            op = cast(
                PutOp,
                handle_patch_memory(
                    namespace,
                    key,
                    format_information(
                        experience, tavily_res=tavily_res, old_value=company.value
                    ),
                    existing_item=None,  # Force new entry
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
                existing_item=None,
                prompt="memory-company",
                schema_model=CompanyInfo,
                config=config,
            ),
        )

        return {
            "experience_enrichment": [cast(CompanyInfo, op.value)],
            "batch_store_ops": [op],
        }
