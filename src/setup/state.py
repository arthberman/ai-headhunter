import uuid
from enum import Enum
from typing import List, Optional, Union

from pydantic import BaseModel, Field

from setup.models.job_posting import JobPosting
from setup.models.question import ListQuestions
from setup.models.scorecard import Scorecard
from setup.models.synthesis import Synthesis


class ResourceOrigin(str, Enum):
    """Enum for different resource origins."""

    HUMAN = "human"  # Directly provided by a human through UI
    AGENT = "agent"  # Auto-scraped by AI agent


class ResourceType(str, Enum):
    """Enum for different resource types."""

    TEXT = "text"
    URL = "url"
    PDF = "pdf"
    QUESTION = "question"
    FEEDBACK = "feedback"


class FeedbackResource(BaseModel):
    """Model for feedback-specific fields."""

    feedback_processed: bool = Field(default=False)


class QuestionResource(BaseModel):
    """Model for question-specific fields."""

    question_id: uuid.UUID = Field(...)


class TextResource(BaseModel):
    """Model for text-specific fields."""

    pass  # Add any text-specific fields here


class URLResource(BaseModel):
    """Model for URL-specific fields."""

    pass  # Add any URL-specific fields here


class PDFResource(BaseModel):
    """Model for PDF-specific fields."""

    pass  # Add any PDF-specific fields here


class BaseResource(BaseModel):
    """Base class for all resource types."""

    source: ResourceOrigin = Field(
        ..., description="Source of the context (human/agent)"
    )
    content_type: ResourceType = Field(..., description="Type of the context")
    content: str = Field(..., description="The actual content")

    # Use discriminated union for type-specific fields
    type_specific: Optional[
        Union[
            FeedbackResource, QuestionResource, TextResource, URLResource, PDFResource
        ]
    ] = None


class ScorecardInputGraphState(BaseModel):
    """State of the scorecard input graph."""

    resources: List[BaseResource] = Field(
        default_factory=list,
        description="List of all resources related to the job posting",
    )

    def get_resources_from_human(self, as_dict: bool = False) -> List[BaseResource]:
        """Get all resources provided by a human."""
        resources = [
            resource
            for resource in self.resources
            if resource.source == ResourceOrigin.HUMAN
        ]
        return [
            resource.model_dump() if as_dict else resource for resource in resources
        ]

    def get_resources_from_agent(self, as_dict: bool = False) -> List[BaseResource]:
        """Get all resources scraped by agents."""
        resources = [
            resource
            for resource in self.resources
            if resource.source == ResourceOrigin.AGENT
        ]
        return [
            resource.model_dump() if as_dict else resource for resource in resources
        ]

    def get_all_resources_without_feedback(
        self, as_dict: bool = False
    ) -> List[BaseResource]:
        """Get all resources without feedback."""
        resources = [
            resource
            for resource in self.resources
            if resource.content_type != ResourceType.FEEDBACK
        ]
        return [
            resource.model_dump() if as_dict else resource for resource in resources
        ]

    def get_text_resources(self, as_dict: bool = False) -> List[BaseResource]:
        """Get all text resources."""
        resources = [
            resource
            for resource in self.resources
            if resource.content_type == ResourceType.TEXT
        ]
        return [
            resource.model_dump() if as_dict else resource for resource in resources
        ]

    def get_url_resources(self, as_dict: bool = False) -> List[BaseResource]:
        """Get all URL resources."""
        resources = [
            resource
            for resource in self.resources
            if resource.content_type == ResourceType.URL
        ]
        return [
            resource.model_dump() if as_dict else resource for resource in resources
        ]

    def get_pdf_resources(self, as_dict: bool = False) -> List[BaseResource]:
        """Get all PDF resources."""
        resources = [
            resource
            for resource in self.resources
            if resource.content_type == ResourceType.PDF
        ]
        return [
            resource.model_dump() if as_dict else resource for resource in resources
        ]

    def get_feedback_resources(self, as_dict: bool = False) -> List[BaseResource]:
        """Get all feedback resources."""
        resources = [
            resource
            for resource in self.resources
            if resource.content_type == ResourceType.FEEDBACK
        ]
        return [
            resource.model_dump() if as_dict else resource for resource in resources
        ]

    def get_feedback_resources_unprocessed(
        self, as_dict: bool = False
    ) -> List[BaseResource]:
        """Get all feedback resources that have not been processed."""
        resources = [
            resource
            for resource in self.resources
            if resource.content_type == ResourceType.FEEDBACK
            and not resource.feedback_processed
        ]
        return [
            resource.model_dump() if as_dict else resource for resource in resources
        ]


class ScorecardGraphState(ScorecardInputGraphState):
    """State of the scorecard graph."""

    job_posting: Optional[JobPosting] = Field(
        None, description="Job posting with all the context provided by the user"
    )
    scorecard: Optional[Scorecard] = Field(
        None, description="Scorecard with all the criteria and questions"
    )
    generated_questions: Optional[ListQuestions] = Field(
        None,
        description="List of questions generated by the LLM and answered by the human",
    )
    synthesis: Optional[Synthesis] = Field(
        None, description="Synthesis of the scorecard"
    )
