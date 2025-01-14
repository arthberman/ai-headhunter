from pydantic import BaseModel, Field
from typing import List, Optional


class JobTitleAnomaly(BaseModel):
    """Model representing an anomaly detected in a job title during validation, including the issue type, affected title, and explanation."""

    issue: str = Field(
        ...,
        description="Type of issue detected: 'Role Alignment Issue', 'Market Usage Issue' or 'Other Issue'.",
    )
    title: str = Field(..., description="The job title that failed the validation.")
    explanation: str = Field(
        ..., description="Brief explanation of why the job title failed the test"
    )


class FeedbackResponse(BaseModel):
    """Response model containing a list of job title anomalies detected during validation."""

    anomalies: List[JobTitleAnomaly] = Field(
        description="List of detected anomalies in job titles. Empty list means no anomalies found.",
        title="Detected Anomalies",
    )
