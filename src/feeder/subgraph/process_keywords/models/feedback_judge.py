from typing import List, Literal

from pydantic import BaseModel, Field


class KeywordsAnomaly(BaseModel):
    """Anomaly detected in the keywords."""

    issue: Literal["Precise Keywords Usage Issue", "Other Issue"] = Field(
        ...,
        description="Type of issue detected: 'Precise Keywords Usage Issue' or 'Other Issue'.",
    )
    title: str = Field(..., description="The keyword that failed the validation.")
    explanation: str = Field(
        ..., description="Brief explanation of why the keyword failed the test"
    )


class FeedbackResponse(BaseModel):
    """Anomalies detected in the keywords."""

    anomalies: List[KeywordsAnomaly] = Field(
        description="List of detected anomalies in keywords. Empty list means no anomalies found.",
        title="Detected Anomalies",
    )
