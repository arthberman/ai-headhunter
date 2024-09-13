from typing import List

from langchain.pydantic_v1 import BaseModel, Field
from langgraph.graph import MessagesState

from scorecard.sub_graph.enrichment.tools import GlobalContext


class EnrichmentGraphState(BaseModel):
    raw_job_posting: str = Field(
        ..., description="Raw job posting with all the context provided by the user"
    )
    global_context: List[str] = Field(..., description="List of context elements")


# Define the AgentState
class AgentState(MessagesState):
    global_context: GlobalContext
