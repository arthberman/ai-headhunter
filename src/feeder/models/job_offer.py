from pydantic import BaseModel, Field


class JobOfferDescription(BaseModel):
    """A structured representation of key job offer attributes used throughout the matching system.

    The separation of summary, seniority, and location serves multiple purposes:
    1. Summary: Contains the detailed job description text used for keyword extraction
       and role understanding
    2. Seniority: Isolated to enable specific filtering in LinkedIn Sales Navigator
       queries and ensure appropriate candidate level matching
    3. Location: Separated to facilitate geographical targeting and regional query
       optimization

    Role in the job matching system:
    1. Serves as the primary input for query generation (see first_gen_raw_query.py)
    2. Used by various subgraphs (keywords, job titles, location) to generate
       optimized search parameters
    3. Provides context for the LLM to understand role requirements and generate
       appropriate search criteria
    """

    summary: str = Field(..., description="Detailed job description text")
    seniority: str = Field(..., description="Seniority level of the job")
    location: str = Field(..., description="Geographical location of the job")
