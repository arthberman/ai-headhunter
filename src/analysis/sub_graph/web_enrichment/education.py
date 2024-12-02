from typing import Optional, cast

from langchain_community.tools import TavilySearchResults
from langchain_core.runnables import RunnableConfig
from langgraph.store.base import BaseStore, PutOp
from pydantic import ValidationError

from analysis.memory.handle_patch_memory import handle_patch_memory
from analysis.memory.models.school import SchoolInfo
from analysis.models.profile import ProfileEducation
from analysis.sub_graph.web_enrichment.state import (
    EducationState,
    MainEnrichmentState,
)

tavily_tool = TavilySearchResults(
    max_results=10, include_answer=True, search_depth="advanced"
)


def format_information(
    education: ProfileEducation,
    tavily_res: Optional[str] = None,
    old_value: Optional[dict] = None,
) -> str:
    """Format input for memory client with optional Tavily search results and old value."""
    information = f"""
        ***candidate_profile***
        School: {education.school}"""

    # Add description only if rich
    if len(education.description) >= 100:
        information += f"""
        Description: {education.description}"""

    information += "\n        ***candidate_profile***"

    # Add Tavily results if provided
    if tavily_res:
        information = f"""
            ***web_search***
            {tavily_res}
            ***web_search***
            {information}"""

    # Add old value if provided
    if old_value:
        information += f"""
            ***old_value***
            {old_value}
            ***old_value***"""

    return information


def node_education_enrichment(
    state: EducationState, *, config: RunnableConfig, store: BaseStore
) -> MainEnrichmentState:
    """Enrich the education of the candidate."""
    education = cast(ProfileEducation, state["education"])

    # If no linkedin_id, return empty
    if not education.linkedin_id:
        return {"education_enrichment": []}

    # Access store
    namespace = ("school", "enrichment")
    key = education.linkedin_id.lower().strip()
    school = store.get(namespace, key)

    if school:
        try:
            # Try to validate against current schema
            school_info = SchoolInfo.model_validate(school.value)

            if len(education.description) < 100:
                return {"education_enrichment": [school_info]}

            # Update with rich description
            op = cast(
                PutOp,
                handle_patch_memory(
                    namespace,
                    key,
                    format_information(education),
                    existing_item=school,
                    prompt="memory-school",
                    schema_model=SchoolInfo,
                    config=config,
                ),
            )
            return {
                "education_enrichment": [cast(SchoolInfo, op.value)],
                "batch_store_ops": [op],
            }
        except ValidationError:
            # Schema mismatch - treat as if not in store and reprocess
            tavily_res = tavily_tool.invoke(
                {"query": f"school {education.school} ({education.linkedin_id})"}
            )

            # Create new entry with current schema
            op = cast(
                PutOp,
                handle_patch_memory(
                    namespace,
                    key,
                    format_information(
                        education, tavily_res=tavily_res, old_value=school.value
                    ),
                    existing_item=None,  # Force new entry
                    prompt="memory-school",
                    schema_model=SchoolInfo,
                    config=config,
                ),
            )
            return {
                "education_enrichment": [cast(SchoolInfo, op.value)],
                "batch_store_ops": [op],
            }
    else:
        # If not in store or cast failed, perform Tavily search
        tavily_res = tavily_tool.invoke(
            {"query": f"school {education.school} ({education.linkedin_id})"}
        )

        op = cast(
            PutOp,
            handle_patch_memory(
                namespace,
                key,
                format_information(education, tavily_res),
                existing_item=None,
                prompt="memory-school",
                schema_model=SchoolInfo,
                config=config,
            ),
        )
        return {
            "education_enrichment": [cast(SchoolInfo, op.value)],
            "batch_store_ops": [op],
        }
