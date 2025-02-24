from typing import List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

from feeder.models.filters_query import FilterQuery
from feeder.models.job_offer import JobOfferDescription
from feeder.models.job_titles_ranking import JobTitlesRankings
from feeder.models.keywords_ranking import KeywordsRankings
from feeder.models.location import LocationData
from feeder.models.people_search_filter import ProfileLanguage
from feeder.models.query_memory import QueryMemory
from feeder.models.raw_query import RawQuery
from feeder.models.seniority_level import SeniorityLevel


class OverallState(BaseModel):
    """State model containing job offer details and derived search parameters.

    Data Flow Through System:
    1. Initial job description (job_offer_description) is processed to extract:
       - Location information (locations)
       - Seniority requirements (seniority_level)
       - Job titles to include/exclude (job_titles_classified)
       - Keywords for search refinement (keywords_classified)

    2. Query Generation and Optimization:
       - Raw queries are generated (json_object)
       - Queries are refined based on feedback (query_results)
       - Progress is tracked (current_query_index)
       - History is maintained (query_memory)

    Optional Fields Explanation:
    - json_object: None until initial query generation
    - seniority_level/locations: None until extracted from job description
    - keywords/include/exclude: None until query refinement
    - classified fields: None until LLM processing complete
    """

    # Primary Input
    job_offer_description: JobOfferDescription = Field(
        ...,
        description="Structured job offer description with summary, seniority and location",
    )
    target_language: Optional[ProfileLanguage] = Field(
        default=ProfileLanguage.ENGLISH,
        description="Language to generate the query keywords in",
    )
    data_source: Literal[
        "crustdata", "linkedin_recruiter", "linkedin_sales_nav", "hellowork"
    ] = Field(
        description="Data source to use for getting profile search count",
    )

    # Initial Query Generation
    json_object: Optional[RawQuery] = Field(None)

    # Location
    locations: Optional[LocationData] = Field(None)

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        from_attributes=True,
    )

    # Classify Job Titles and Keywords
    job_titles_classified: Optional[JobTitlesRankings] = Field(None)
    keywords_classified: Optional[KeywordsRankings] = Field(
        default=None,
        description="Classification of keywords into FAR and NEAR categories",
    )

    # Optimization State
    query_results: Optional[List[FilterQuery]] = Field(default_factory=list)

    # Query Memory
    query_memory: Optional[QueryMemory] = Field(None)
    global_iteration_count: int = Field(
        default=0, description="Counter for global feedback iterations"
    )


class OverallInputState(BaseModel):
    """Input state model containing job offer description.

    This is the initial state that starts the processing pipeline.
    All other fields are derived from this primary input through
    various processing steps (see KeywordsState, LocationSubGraphState, etc.)
    """

    # job_offer_description: JobOfferDescription = Field(...)
    raw_job_description: str = Field(..., description="Raw job description text")
    target_language: Optional[ProfileLanguage] = Field(
        default=ProfileLanguage.ENGLISH,
        description="Language to generate the query keywords in",
    )
    data_source: Literal["crustdata", "linkedin_recruiter", "linkedin_sales_nav"] = (
        Field(..., description="Data source to use for getting profile search count")
    )


class OverallOutputState(BaseModel):
    """Output state model containing Sales Navigator queries and search parameters.

    Represents the final processed state ready for query execution.
    Contains only the essential fields needed for search:
    - Geographical targeting (locations)
    - Experience level filtering (seniority_level)
    - Role matching criteria (job_titles_classified)
    - Skill/technology requirements (keywords_classified)
    """

    locations: Optional[LocationData] = Field(None)
    seniority_level: Optional[SeniorityLevel] = Field(None)
    job_titles_classified: Optional[JobTitlesRankings] = Field(None)
    keywords_classified: Optional[KeywordsRankings] = Field(None)
    query_results: Optional[List[FilterQuery]] = Field(default_factory=list)
