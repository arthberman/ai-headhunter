from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union, cast

from langchain_community.tools import TavilySearchResults
from langchain_core.runnables import Runnable, RunnableConfig
from langchain_core.tools import BaseTool
from langgraph.prebuilt import InjectedState
from pydantic import BaseModel, Field
from typing_extensions import Annotated

from analysis.configuration import Configuration
from analysis.sub_graph.criterion_analysis.models import ScoredCriterion
from analysis.sub_graph.criterion_analysis.state import AnalysisMainState
from utils import (
    FewShotConfig,
    format_data,
    get_few_shot_messages,
    get_prompt,
    init_model,
)


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
    INDUSTRY_SECTOR = "industry_sector"
    COMPANY_CULTURE = "company_culture"


def get_candidate_info(
    infotype: CandidateInfoType,
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
        CandidateInfoType.COMPANY_CULTURE: state.main_state.inferred_culture,
        CandidateInfoType.INDUSTRY_SECTOR: state.main_state.inferred_sector,
    }

    if infotype not in info_map:
        raise ValueError(f"Invalid infotype: {infotype}")

    data = info_map[infotype]

    if not data:
        return f"No information available for {infotype.value.upper()}. The candidate's profile does not contain any data for this category."
    return format_data(data)


def search_web(query: str, *, config: RunnableConfig) -> Optional[list[dict[str, Any]]]:
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
        """Judge if a query is relevant to a web search."""

        relevant: bool = Field(
            ..., description="Whether the query is relevant to the search results"
        )

    # Initialize the configuration
    configuration = Configuration.from_runnable_config(config)

    # Initialize the prompt
    prompt = get_prompt("judge-web-search")

    # Initialize the model
    raw_model = init_model(configuration.default_model)
    model = raw_model.with_structured_output(JudgeWebSearch)

    # Create the chain
    chain = cast(Runnable, prompt | model)

    # Few shots
    few_shot_config = FewShotConfig(
        dataset_name="fs-judge-web-search",
        input_keys=["web_query"],
        output_keys=["is_relevant", "explanation"],
        input_template="Web query: {web_query}",
        output_template="Is relevant: {is_relevant}\nExplanation: {explanation}",
    )
    few_shot_messages = get_few_shot_messages(few_shot_config)

    # Invoke the chain
    res = cast(
        JudgeWebSearch,
        chain.invoke(
            {
                "web_query": query,
                "examples": few_shot_messages,
                "system_time": datetime.now().strftime("%d %B %Y (%d-%m-%Y)"),
                "output_language": configuration.output_language,
            }
        ),
    )

    if not res.relevant:
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
