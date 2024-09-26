import operator
from typing import Annotated, Optional, Sequence

from langchain import hub
from langchain_core.messages import AIMessage, BaseMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableConfig
from langgraph.errors import NodeInterrupt
from pydantic import BaseModel, Field

from scorecard_generator.configuration import Configuration
from scorecard_generator.sub_graph.enrichment.tools import WebContext, get_tools
from scorecard_generator.utils import init_model


class AgentState(BaseModel):
    """State of the agent."""

    messages: Annotated[Sequence[BaseMessage], operator.add]
    raw_job_posting: str = Field(
        ..., description="Raw job posting with all the context provided by the user"
    )
    web_context: Optional[WebContext] = Field(
        None, description="Web context for the job posting"
    )
    loop_step: Annotated[int, operator.add] = Field(default=0)


def init_agent(state: AgentState):
    """Initialize the agent."""
    hub_prompt = hub.pull("generate-scorecard-enrichment")

    chat_prompt = ChatPromptTemplate.from_messages(hub_prompt.messages)

    formatted_messages = chat_prompt.format_messages(
        raw_job_posting=state.raw_job_posting
    )

    return {"messages": formatted_messages}


def call_model(state: AgentState, *, config: Optional[RunnableConfig] = None):
    """Call the model."""
    # Load configuration from the provided RunnableConfig
    configuration = Configuration.from_runnable_config(config)

    # Check if the loop step is greater than the maximum number of loops
    if state.loop_step == configuration.max_loops - 1:
        return {
            "messages": [
                AIMessage(
                    content="You exceeded the maximum number of loops. You must respond to the user by calling the WebContext tool now.",
                )
            ],
            "loop_step": 1,
        }

    # Initialize the raw model with the provided configuration and bind the tools
    raw_model = init_model(configuration.enrichment_model)

    # Bind the tools to the model
    model = raw_model.bind_tools(get_tools(), tool_choice="any")
    response = model.invoke(state.messages)
    return {"messages": [response], "loop_step": 1}


def respond(state: AgentState):
    """Respond to the user."""
    response = WebContext(**state.messages[-1].tool_calls[0]["args"])
    # We return the final answer
    return {"web_context": response.web_context}


def should_continue(state: AgentState, *, config: Optional[RunnableConfig] = None):
    """Determine whether to continue or not."""
    # Load configuration from the provided RunnableConfig
    configuration = Configuration.from_runnable_config(config)

    # Check if the loop step is exceeding the maximum number of loops
    if state.loop_step >= configuration.max_loops + 3:
        raise NodeInterrupt("The loop step exceeded the maximum number of loops")

    messages = state.messages
    last_message = messages[-1]
    # If there is only one tool call and it is the response tool call we respond to the user
    if (
        len(last_message.tool_calls) == 1
        and last_message.tool_calls[0]["name"] == "WebContext"
    ):
        return "respond"
    # Otherwise we will use the tool node again
    else:
        return "continue"
