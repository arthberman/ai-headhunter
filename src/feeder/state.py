from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field

from feeder.models.filters_query import FilterQuery
from feeder.models.job_offer import JobOfferDescription
from feeder.models.job_titles_ranking import JobTitlesRankings
from feeder.models.query_memory import QueryMemory
from feeder.models.raw_query import RawQuery
from src.feeder.models.keywords_ranking import KeywordsRankings
from src.feeder.models.location import LocationItem
from src.feeder.models.seniority_level import SeniorityLevel


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
    job_offer_description: JobOfferDescription = Field(...)

    # Initial Query Generation
    json_object: Optional[RawQuery] = Field(None)
    seniority_level: Optional[SeniorityLevel] = Field(None)
    real_job_title: Optional[str] = Field(None)
    keywords: Optional[List[str]] = Field(None)

    # Location and Filter Parameters
    locations: Optional[List[LocationItem]] = Field(None)
    include: Optional[List[str]] = Field(None)
    exclude: Optional[List[str]] = Field(None)

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        from_attributes=True,
    )

    # Classification and Optimization State
    job_titles_classified: Optional[JobTitlesRankings] = Field(None)
    keywords_classified: Optional[KeywordsRankings] = Field(
        default=None,
        description="Classification of keywords into FAR and NEAR categories",
    )
    query_results: Optional[List[FilterQuery]] = Field(default_factory=list)
    current_query_index: Optional[int] = Field(default=0)
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

    job_offer_description: JobOfferDescription = Field(...)


class OverallOutputState(BaseModel):
    """Output state model containing Sales Navigator queries and search parameters.

    Represents the final processed state ready for query execution.
    Contains only the essential fields needed for search:
    - Geographical targeting (locations)
    - Experience level filtering (seniority_level)
    - Role matching criteria (job_titles_classified)
    - Skill/technology requirements (keywords_classified)
    """

    locations: Optional[List[LocationItem]] = Field(None)
    seniority_level: Optional[SeniorityLevel] = Field(None)
    job_titles_classified: Optional[JobTitlesRankings] = Field(None)
    keywords_classified: Optional[KeywordsRankings] = Field(None)
    query_results: Optional[List[FilterQuery]] = Field(default_factory=list)
