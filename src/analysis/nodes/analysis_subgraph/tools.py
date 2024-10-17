# First we initialize the model we want to use.
import os
from enum import Enum
from typing import Any, Dict, List, Optional, Union, cast

from langchain_community.tools import TavilySearchResults
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import BaseTool
from langgraph.prebuilt import InjectedState
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from typing_extensions import Annotated

from analysis.iterative.configuration import Configuration
from analysis.models.knowledge_point import (
    KnowledgePoint,
    KnowledgePointDB,
)
from analysis.nodes.analysis_subgraph.models import ScoredCriterion
from analysis.nodes.analysis_subgraph.state import AnalysisMainState
from scorecard.models.scorecard import CriterionType
from utils import format_data


class CandidateInfoType(Enum):
    """The type of information to get about the candidate."""

    EXPERIENCES = "experiences"
    SKILLS = "skills"
    CERTIFICATIONS = "certifications"
    EDUCATIONS = "educations"
    HONORS = "honors"
    LANGUAGES = "languages"
    PROJECTS = "projects"
    VOLUNTEERINGS = "volunteerings"


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
            "language_enrichment": [
                language_enrichment.model_dump()
                for language_enrichment in state.main_state.language_enrichment
            ],
        },
        CandidateInfoType.PROJECTS: [
            project.model_dump() for project in state.main_state.profile.projects
        ],
        CandidateInfoType.VOLUNTEERINGS: [
            volunteering.model_dump()
            for volunteering in state.main_state.profile.volunteerings
        ],
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
    """Query a search engine for general information not related to specific candidates.

    This function queries the web to fetch comprehensive, accurate, and trusted results about general topics.
    It's particularly useful for answering questions about current events, general knowledge, or industry trends.

    Important:
    - Do NOT use this tool for any candidate-specific information or queries.
    - Do NOT use this tool for information about job requirements, scorecards, or the hiring process.
    - Instead, use the `get_candidate_info` tool for candidate-specific data.
    - For scorecard or job requirement information, refer to the provided context or use appropriate tools.
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
        get_knowledge_points,
    ]
    return tools


def get_knowledge_points(criterion_types: list[CriterionType]) -> list[KnowledgePoint]:
    """Retrieve knowledge base entries by a list of criterion types.

    This function should be called at the beginning of the process to obtain knowledge points relevant to the specified criterion types.
    If the item to score involves multiple criteria (e.g., language and experience), this function should be called with a list of criterion types.
    """
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise ValueError("DATABASE_URL environment variable is not set")
    engine = create_engine(database_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()

    try:
        stmt = select(KnowledgePointDB).where(
            KnowledgePointDB.type.in_(criterion_types)
        )
        result = session.execute(stmt).scalars().all()
        knowledge_points = [
            KnowledgePoint(type=kp.type, description=kp.description) for kp in result
        ]  # Convert to KnowledgePoint with only type and description
    finally:
        session.close()

    return knowledge_points
