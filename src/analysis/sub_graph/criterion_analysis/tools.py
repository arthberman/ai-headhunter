# First we initialize the model we want to use.
import os
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union, cast

from langchain import hub
from langchain_community.tools import TavilySearchResults
from langchain_core.runnables import Runnable, RunnableConfig
from langchain_core.tools import BaseTool
from langgraph.prebuilt import InjectedState
from pyairtable import Api
from pydantic import BaseModel, Field
from typing_extensions import Annotated

from analysis.iterative.configuration import Configuration
from analysis.models.knowledge_point import (
    KnowledgePoint,
)
from analysis.sub_graph.criterion_analysis.models import ScoredCriterion
from analysis.sub_graph.criterion_analysis.state import AnalysisMainState
from scorecard.models.scorecard import CriterionType
from utils import format_data, init_model


class CandidateInfoType(Enum):
    """The type of information to get about the candidate."""

    EXPERIENCES = "EXPERIENCES"
    SKILLS = "SKILLS"
    CERTIFICATIONS = "CERTIFICATIONS"
    EDUCATIONS = "EDUCATIONS"
    HONORS = "HONORS"
    LANGUAGES = "LANGUAGES"
    PROJECTS = "PROJECTS"
    VOLUNTEERINGS = "VOLUNTEERINGS"
    CULTURE = "CULTURE"
    SECTOR = "SECTOR"


def get_candidate_info(
    info_type: CandidateInfoType,
    state: Annotated[AnalysisMainState, InjectedState],
) -> Union[List[Dict[str, Any]], List[str], Dict[str, Any], str]:
    """Get specific information about the candidate."""
    info_map = {
        CandidateInfoType.EXPERIENCES: {
            "experiences": [
                experience.model_dump()
                for experience in state.main_state.profile.experiences
            ],
            "experience_enrichment": [
                experience_enrichment.model_dump()
                for experience_enrichment in state.main_state.experience_enrichment
            ],
        },
        CandidateInfoType.SKILLS: state.main_state.profile.skills,
        CandidateInfoType.CERTIFICATIONS: [
            certification.model_dump()
            for certification in state.main_state.profile.certifications
        ],
        CandidateInfoType.EDUCATIONS: {
            "educations": [
                education.model_dump()
                for education in state.main_state.profile.educations
            ],
            "education_enrichment": [
                education_enrichment.model_dump()
                for education_enrichment in state.main_state.education_enrichment
            ],
        },
        CandidateInfoType.HONORS: [
            honor.model_dump() for honor in state.main_state.profile.honors
        ],
        CandidateInfoType.LANGUAGES: {
            "languages": [
                language.model_dump() for language in state.main_state.profile.languages
            ],
            "inferred_languages": [
                inferred_languages.model_dump()
                for inferred_languages in state.main_state.inferred_languages
            ],
        },
        CandidateInfoType.PROJECTS: [
            project.model_dump() for project in state.main_state.profile.projects
        ],
        CandidateInfoType.VOLUNTEERINGS: [
            volunteering.model_dump()
            for volunteering in state.main_state.profile.volunteerings
        ],
        CandidateInfoType.CULTURE: state.main_state.inferred_culture,
        CandidateInfoType.SECTOR: state.main_state.inferred_sector,
    }

    if info_type not in info_map:
        raise ValueError(f"Invalid info_type: {info_type}")

    data = info_map[info_type]

    if not data:
        return f"No information available for {info_type.value.upper()}. The candidate's profile does not contain any data for this category."

    return format_data(data)


def search_web(
    query: str, *, config: Optional[RunnableConfig] = None
) -> Optional[list[dict[str, Any]]]:
    """Query a search engine.

    This function queries the web to fetch comprehensive, accurate, and trusted results. It's particularly useful
    for answering questions about current events. Provide as much context in the query as needed to ensure high recall.

    Important:
    - Do NOT use this tool for any candidate-specific information or queries.
    - Do NOT use this tool for information about job requirements, scorecards, or the hiring process.
    - Instead, use the `get_candidate_info` tool for candidate-specific data.
    - For scorecard or job requirement information, refer to the provided context.
    """

    class JudgeWebSearch(BaseModel):
        is_relevant: bool = Field(
            ..., description="Whether the query is relevant to the search results"
        )

    configuration = Configuration.from_runnable_config(config)
    prompt = hub.pull("judge-web-search:production")
    raw_model = init_model("openai/gpt-4o-mini")
    model = raw_model.with_structured_output(JudgeWebSearch)
    chain = cast(Runnable, prompt | model)
    res = cast(
        JudgeWebSearch,
        chain.invoke(
            {
                "web_query": query,
                "system_time": datetime.now().isoformat(),
                "output_schema": JudgeWebSearch.model_json_schema(),
                "output_language": configuration.output_language,
            }
        ),
    )

    if not res.is_relevant:
        return "The query is not relevant for a web search."

    wrapped = TavilySearchResults(max_results=configuration.max_search_results)
    result = wrapped.invoke({"query": query})
    return cast(list[dict[str, Any]], result)


def get_tools() -> List[BaseTool]:
    """Get the list of available tools for the analysis graph.

    Returns:
        A list of BaseTool instances.
    """
    tools = [
        ScoredCriterion,
        search_web,
        get_candidate_info,
    ]
    return tools


def get_knowledge_points(types: list[CriterionType]) -> list[KnowledgePoint]:
    """Retrieve knowledge base entries by a list of criterion types."""
    api = Api(os.environ["AIRTABLE_API_KEY"])
    table = api.table("appnlCNqfC0erFVX7", "tbl7TLnZwMynf8pjJ")

    # Construct the OR formula for multiple criterion types
    criterion_conditions = [f"{{CriterionType}} = '{ct.value}'" for ct in types]
    formula = f"OR({','.join(criterion_conditions)})"

    # Fetch filtered records
    filtered_records = table.all(formula=formula)

    # Convert Airtable records to KnowledgePoint objects
    knowledge_points = [
        KnowledgePoint(
            type=CriterionType(record["fields"]["CriterionType"]),
            description=record["fields"]["Description"],
        )
        for record in filtered_records
    ]

    return knowledge_points
