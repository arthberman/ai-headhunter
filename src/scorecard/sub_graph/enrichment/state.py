from typing import List

from pydantic import BaseModel, Field
from langgraph.graph import MessagesState

from scorecard.sub_graph.enrichment.tools import WebContext


class EnrichmentGraphState(BaseModel):
    raw_job_posting: str = Field(
        ..., description="Raw job posting with all the context provided by the user"
    )
    web_context: List[str] = Field(..., description="List of context elements")


# Define the AgentState
class AgentState(MessagesState):
    web_context: WebContext
