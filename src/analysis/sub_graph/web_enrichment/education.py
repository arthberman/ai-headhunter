from datetime import datetime
from typing import cast

from langchain_community.tools import TavilySearchResults
from langchain_core.runnables import Runnable, RunnableConfig
from langgraph.store.base import BaseStore

from analysis.full.configuration import Configuration
from analysis.models.profile import ProfileEducation
from analysis.models.school import SchoolInfo
from analysis.sub_graph.web_enrichment.state import (
    EducationState,
    OutputEnrichmentState,
)
from utils import get_prompt, init_model

tavily_tool = TavilySearchResults(
    max_results=10, include_answer=True, search_depth="advanced"
)


def node_education_enrichment(
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
    namespace = ("school", "web_enrichment")
    key = education.linkedin_url.rstrip("/").split("/")[-1].lower().strip()
    school = store.get(namespace, key)

    if school:
        return {"education_enrichment": [SchoolInfo(**school.value)]}

    # If not in database, perform Tavily search
    tavily_res = tavily_tool.invoke(
        {"query": f"school {education.school} ({education.linkedin_url})"}
    )
    prompt = get_prompt("generate-education-enrichment")

    # Initialize the chat model with the provided configuration
    raw_model = init_model(configuration.enrichment_model)
    model = raw_model.with_structured_output(SchoolInfo)

    chain = cast(Runnable, prompt | model)
    res = cast(
        SchoolInfo,
        chain.invoke(
            {
                "web_browsing_result": tavily_res,
                "school": education.school,
                "school_description": education.description,
                "linkedin_url": education.linkedin_url,
                "output_schema": SchoolInfo.model_json_schema(),
                "output_language": configuration.output_language,
                "system_time": datetime.now().strftime("%Y-%m-%d (Y-m-d)"),
            }
        ),
    )

    # Add the new school info to the database
    store.put(namespace, key, res)

    return {"education_enrichment": [res]}
