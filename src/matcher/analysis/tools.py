# First we initialize the model we want to use.
from enum import Enum
from typing import Any, Dict, List, Optional, Union, cast

from langchain_community.tools import TavilySearchResults
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import BaseTool, tool
from langgraph.prebuilt import InjectedState
from typing_extensions import Annotated

from matcher.analysis.models import ScoredCriterion
from matcher.analysis.state import AnalysisMainState
from matcher.configuration import Configuration
from utils.format import format_data


class CandidateInfoType(Enum):
    EXPERIENCES = "experiences"
    SKILLS = "skills"
    CERTIFICATIONS = "certifications"
    EDUCATIONS = "educations"
    HONORS = "honors"
    LANGUAGES = "languages"
    PROJECTS = "projects"
    VOLUNTEERINGS = "volunteerings"
    EDUCATION_ENRICHMENT = "education_enrichment"
    EXPERIENCE_ENRICHMENT = "experience_enrichment"
    LANGUAGE_ENRICHMENT = "language_enrichment"


def get_candidate_info(
    info_type: CandidateInfoType,
    state: Annotated[AnalysisMainState, InjectedState],
) -> Union[List[Dict[str, Any]], List[str], Dict[str, Any]]:
    """Get specific information about the candidate."""
    info_map = {
        CandidateInfoType.EXPERIENCES: {
            "experiences": state.main_state.profile.experiences,
            "experience_enrichment": state.main_state.experience_enrichment,
        },
        CandidateInfoType.SKILLS: state.main_state.profile.skills,
        CandidateInfoType.CERTIFICATIONS: state.main_state.profile.certifications,
        CandidateInfoType.EDUCATIONS: {
            "educations": state.main_state.profile.educations,
            "education_enrichment": state.main_state.education_enrichment,
        },
        CandidateInfoType.HONORS: state.main_state.profile.honors,
        CandidateInfoType.LANGUAGES: {
            "languages": state.main_state.profile.languages,
            "language_enrichment": state.main_state.language_enrichment,
        },
        CandidateInfoType.PROJECTS: state.main_state.profile.projects,
        CandidateInfoType.VOLUNTEERINGS: state.main_state.profile.volunteerings,
        CandidateInfoType.EDUCATION_ENRICHMENT: state.main_state.education_enrichment,
        CandidateInfoType.EXPERIENCE_ENRICHMENT: state.main_state.experience_enrichment,
        CandidateInfoType.LANGUAGE_ENRICHMENT: state.main_state.language_enrichment,
    }

    if info_type not in info_map:
        raise ValueError(f"Invalid info_type: {info_type}")

    return format_data(info_map[info_type])


def search_web(
    query: str, *, config: Optional[RunnableConfig] = None
) -> Optional[list[dict[str, Any]]]:
    """Query a search engine.

    This function queries the web to fetch comprehensive, accurate, and trusted results. It's particularly useful
    for answering questions about current events. Provide as much context in the query as needed to ensure high recall.
    """
    configuration = Configuration.from_runnable_config(config)
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
