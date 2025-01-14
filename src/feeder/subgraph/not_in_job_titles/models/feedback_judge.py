from typing import List, Optional

from pydantic import BaseModel, Field


class NotInJobTitleAnomaly(BaseModel):
    """Represents a validaiton issue found in a job title that should be excluded."""
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
    """Container for a list of job title validation anomalies."""
    anomalies: List[NotInJobTitleAnomaly] = Field(
        description="List of detected anomalies in the list of job titles to exclude. Empty list means no anomalies found.",
        title="Detected Anomalies",
    )
