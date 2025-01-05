from langchain_core.messages import AIMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableConfig
from langgraph.errors import NodeInterrupt

from setup.configuration import Configuration
from setup.nodes.enrichment_subgraph.state import AgentState
from setup.nodes.enrichment_subgraph.tools import WebResource, get_tools
from setup.state import BaseResource, ResourceOrigin, ResourceType
from utils import get_prompt, init_model


def init_agent(state: AgentState):
    """Initialize the agent."""
    hub_prompt = get_prompt("generate-scorecard-enrichment")

    chat_prompt = ChatPromptTemplate.from_messages(hub_prompt.messages)

    formatted_messages = chat_prompt.format_messages(resources=state.resources)

    return {"messages": formatted_messages}


def call_model(state: AgentState, *, config: RunnableConfig):
    """Call the model."""
    # Load configuration from the provided RunnableConfig
    configuration = Configuration.from_runnable_config(config)

    # Check if the loop step is greater than the maximum number of loops
    if state.loop_step == configuration.max_loops - 1:
        return {
            "messages": [
                AIMessage(
                    content="You exceeded the maximum number of loops. You must respond to the user by calling the WebResource tool now.",
                )
            ],
            "loop_step": 1,
        }

    # Initialize the raw model with the provided configuration and bind the tools
    raw_model = init_model(configuration.enrichment_model)

    # Bind the tools to the model
    model = raw_model.bind_tools(get_tools())
    response = model.invoke(state.messages)
    return {"messages": [response], "loop_step": 1}


def respond(state: AgentState):
    """Respond to the user."""
    response = WebResource(**state.messages[-1].tool_calls[0]["args"])

    # Create a list of BaseResource objects from the enriched resources
    enriched_resources = [
        BaseResource(
            source=ResourceOrigin.AGENT,
            content_type=ResourceType.TEXT,
            content=resource,
        )
        for resource in response.resources_enriched
    ]

    state.resources.extend(enriched_resources)

    return {"resources": state.resources}


def should_continue(state: AgentState, *, config: RunnableConfig):
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
        and last_message.tool_calls[0]["name"] == "WebResource"
    ):
        return "respond"
    # Otherwise we will use the tool node again
    else:
        return "continue"
