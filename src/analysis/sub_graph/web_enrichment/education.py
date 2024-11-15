from typing import Optional, cast

from langchain_community.tools import TavilySearchResults
from langchain_core.runnables import RunnableConfig
from langgraph.store.base import BaseStore, PutOp

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
) -> str:
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

    return information


def node_education_enrichment(
    state: EducationState, *, config: RunnableConfig, store: BaseStore
) -> MainEnrichmentState:
    """Enrich the education of the candidate."""
    education = cast(ProfileEducation, state["education"])

    # If no linkedin_url or invalid format, return empty
    if not education.linkedin_url or not education.linkedin_url.startswith(
        "https://www.linkedin.com/school/"
    ):
        return {"education_enrichment": []}

    # Access store
    namespace = ("school", "enrichment")
    key = education.linkedin_url.rstrip("/").split("/")[-1].lower().strip()
    school = store.get(namespace, key)

    if school:
        school_info = cast(SchoolInfo, school.value)
        if len(education.description) < 100:
            return {"education_enrichment": [school_info]}

        # If the description is rich, we can enrich the school info
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
    else:
        # If not in store or cast failed, perform Tavily search
        tavily_res = tavily_tool.invoke(
            {"query": f"school {education.school} ({education.linkedin_url})"}
        )

        op = cast(
            PutOp,
            handle_patch_memory(
                namespace,
                key,
                format_information(education, tavily_res),
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
