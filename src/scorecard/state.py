from typing import List, Optional
from langchain.pydantic_v1 import BaseModel, Field

from scorecard.models.question import Question
from scorecard.sub_graph.enrichment.state import GlobalContext


class ScorecardGraphState(BaseModel):
    raw_job_posting: str = Field(
        ..., description="Raw job posting with all the context provided by the user"
    )
    global_context: Optional[List[str]] = Field(
        description="List of context elements from the web search"
    )
    questions: Optional[List[Question]] = Field(
        description="List of questions for human in the loop"
    )


class ScorecardInputGraphState(BaseModel):
    raw_job_posting: str = Field(
        ..., description="Raw job posting with all the context provided by the user"
    )
