from typing import TypedDict, cast

from langchain_core.messages import AIMessage
from langgraph.graph import END, START, StateGraph
from langgraph.graph.graph import CompiledGraph
from pydantic import BaseModel, Field

from feedback_chat.prompt import system_prompt
from feedback_chat.state import FeedbackChatGraphState, FeedbackChatInputGraphState
from utils import get_retry_policy, init_model


async def chat_feedback(state: FeedbackChatGraphState) -> FeedbackChatGraphState:
    """Node for the feedback chat."""
    raw_model = init_model("openai/gpt-4o")

    class Output(BaseModel):
        """Output of the feedback chat."""

        chat_response: str = Field(
            description="The response to the feedback. Max 300 characters, it must be concise and to the point.",
            alias="chatResponse",
        )
        rules_met: bool = Field(
            description="Whether the feedback rules were met.",
            alias="rulesMet",
        )

    model = raw_model.with_structured_output(Output)

    # prompt from the file system to prevent latency
    prompt = system_prompt.format(
        selected_elements=state.selected_elements,
        overall_profile_context=state.profile,
        job_context=state.job_synthesis,
    )

    messages = [{"role": "system", "content": prompt}] + state.messages
    response = cast(Output, await model.ainvoke(messages))

    return {
        "messages": [AIMessage(content=response.chat_response)],
        "rules_met": response.rules_met,
    }


def compile_feedback_chat_graph() -> CompiledGraph:
    """Compile the feedback chat graph."""
    workflow = StateGraph(FeedbackChatGraphState, input=FeedbackChatInputGraphState)

    workflow.add_node("chat", chat_feedback, retry=get_retry_policy())

    workflow.add_edge(START, "chat")
    workflow.add_edge("chat", END)

    graph = workflow.compile()
    graph.name = "FeedbackChatGraph"
    return graph
