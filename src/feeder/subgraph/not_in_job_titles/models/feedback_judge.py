from typing import List, Optional

from pydantic import BaseModel, Field


class NotInJobTitleAnomaly(BaseModel):
    """Represents a validation issue found in a job title that should be excluded.

    Types of Anomalies:
    1. NotInJobTitle Usage Issue: Occurs when a job title is:
       - Too broad (e.g., "Developer" when excluding junior roles)
       - Too specific (e.g., "Senior Full Stack Developer" when excluding junior roles)
       - Potentially excluding valid candidates

    2. Other Issue: Catches validation problems like:
       - Malformed job titles
       - Non-standard industry terms
       - Titles that conflict with search objectives
    """

    issue: str = Field(
        ...,
        description="Type of issue detected: 'NotInJobTitle Usage Issue' or 'Other Issue'.",
        pattern="^(NotInJobTitle Usage Issue|Other Issue)$",
    )
    title: str = Field(
        ..., description="The job title to exclude that failed the validation."
    )
    explanation: str = Field(
        ...,
        description="Brief explanation of why the job title to exclude failed the test",
    )


class FeedbackResponse(BaseModel):
    """Container for a list of job title validation anomalies.

    Role in the Feedback System:
    1. Collects validation results from the LLM judge (see judge_existing_not_in_job_titles.py)
    2. Provides structured feedback for query optimization
    3. Helps maintain quality control over exclusion filters

    Validation Process:
    1. Job titles are evaluated by an LLM against the job description context
    2. Each problematic title generates a NotInJobTitleAnomaly
    3. Anomalies are used to:
       - Remove problematic exclusions
       - Refine overly broad/specific titles
       - Improve search query precision
    """

    anomalies: List[NotInJobTitleAnomaly] = Field(
        description="List of detected anomalies in the list of job titles to exclude. Empty list means no anomalies found.",
        title="Detected Anomalies",
    )
