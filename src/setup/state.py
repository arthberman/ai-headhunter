import uuid
from enum import Enum
from typing import List, Optional, Union

from pydantic import BaseModel, Field

from setup.models.job_posting import JobPosting
from setup.models.question import ListQuestions
from setup.models.scorecard import Scorecard
from setup.models.synthesis import Synthesis


class ContextSource(str, Enum):
    """Enum for different context sources."""

    HUMAN = "human"  # Directly provided by a human through UI
    AGENT = "agent"  # Auto-scraped by AI agent


class ContextType(str, Enum):
    """Enum for different context types."""

    TEXT = "text"
    URL = "url"
    PDF = "pdf"
    QUESTION = "question"
    FEEDBACK = "feedback"


class FeedbackContext(BaseModel):
    """Model for feedback-specific fields."""

    feedback_processed: bool = Field(default=False)


class QuestionContext(BaseModel):
    """Model for question-specific fields."""

    question_id: uuid.UUID = Field(...)


class TextContext(BaseModel):
    """Model for text-specific fields."""

    pass  # Add any text-specific fields here


class URLContext(BaseModel):
    """Model for URL-specific fields."""

    pass  # Add any URL-specific fields here


class PDFContext(BaseModel):
    """Model for PDF-specific fields."""

    pass  # Add any PDF-specific fields here


class BaseContext(BaseModel):
    """Base class for all context types."""

    source: ContextSource = Field(
        ..., description="Source of the context (human/agent)"
    )
    content_type: ContextType = Field(..., description="Type of the context")
    content: str = Field(..., description="The actual content")

    # Use discriminated union for type-specific fields
    type_specific: Optional[
        Union[FeedbackContext, QuestionContext, TextContext, URLContext, PDFContext]
    ] = None


class ScorecardInputGraphState(BaseModel):
    """State of the scorecard input graph."""

    contexts: List[BaseContext] = Field(
        default_factory=list,
        description="List of all context objects related to the job posting",
    )

    def get_contexts_from_human(self, as_dict: bool = False) -> List[BaseContext]:
        """Get all contexts provided by a human."""
        contexts = [ctx for ctx in self.contexts if ctx.source == ContextSource.HUMAN]
        return [ctx.model_dump() if as_dict else ctx for ctx in contexts]

    def get_contexts_from_agent(self, as_dict: bool = False) -> List[BaseContext]:
        """Get all contexts scraped by agents."""
        contexts = [ctx for ctx in self.contexts if ctx.source == ContextSource.AGENT]
        return [ctx.model_dump() if as_dict else ctx for ctx in contexts]

    def get_all_contexts_without_feedback(
        self, as_dict: bool = False
    ) -> List[BaseContext]:
        """Get all contexts without feedback."""
        contexts = [
            ctx for ctx in self.contexts if ctx.content_type != ContextType.FEEDBACK
        ]
        return [ctx.model_dump() if as_dict else ctx for ctx in contexts]

    def get_text_contexts(self, as_dict: bool = False) -> List[BaseContext]:
        """Get all text contexts."""
        contexts = [
            ctx for ctx in self.contexts if ctx.content_type == ContextType.TEXT
        ]
        return [ctx.model_dump() if as_dict else ctx for ctx in contexts]

    def get_url_contexts(self, as_dict: bool = False) -> List[BaseContext]:
        """Get all URL contexts."""
        contexts = [ctx for ctx in self.contexts if ctx.content_type == ContextType.URL]
        return [ctx.model_dump() if as_dict else ctx for ctx in contexts]

    def get_pdf_contexts(self, as_dict: bool = False) -> List[BaseContext]:
        """Get all PDF contexts."""
        contexts = [ctx for ctx in self.contexts if ctx.content_type == ContextType.PDF]
        return [ctx.model_dump() if as_dict else ctx for ctx in contexts]

    def get_feedback_contexts(self, as_dict: bool = False) -> List[BaseContext]:
        """Get all feedback contexts."""
        contexts = [
            ctx for ctx in self.contexts if ctx.content_type == ContextType.FEEDBACK
        ]
        return [ctx.model_dump() if as_dict else ctx for ctx in contexts]

    def get_feedback_contexts_unprocessed(
        self, as_dict: bool = False
    ) -> List[BaseContext]:
        """Get all feedback contexts that have not been processed."""
        contexts = [
            ctx
            for ctx in self.contexts
            if ctx.content_type == ContextType.FEEDBACK and not ctx.feedback_processed
        ]
        return [ctx.model_dump() if as_dict else ctx for ctx in contexts]


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


# deleted fields : context_enriched, context_additional, context_initial, human_feedback
