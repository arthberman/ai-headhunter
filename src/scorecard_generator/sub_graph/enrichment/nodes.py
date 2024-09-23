from langchain import hub
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langgraph.graph import MessagesState

from scorecard_generator.sub_graph.enrichment.tools import WebContext, get_tools


class AgentState(MessagesState):
    """State of the agent."""

    raw_job_posting: str
    web_context: WebContext


def init_agent(state: AgentState):
    """Initialize the agent."""
    hub_prompt = hub.pull("generate-scorecard-enrichment")

    chat_prompt = ChatPromptTemplate.from_messages(hub_prompt.messages)

    formatted_messages = chat_prompt.format_messages(
        raw_job_posting=state["raw_job_posting"]
    )

    return {"messages": formatted_messages}


def call_model(state: AgentState):
    """Call the model."""
    model_with_response_tool = ChatOpenAI(
        model="gpt-4o-mini", temperature=0
    ).bind_tools(get_tools(), tool_choice="any", parallel_tool_calls=False)

    response = model_with_response_tool.invoke(state["messages"])
    return {"messages": [response]}


def respond(state: AgentState):
    """Respond to the user."""
    response = WebContext(**state["messages"][-1].tool_calls[0]["args"])
    # We return the final answer
    return {"web_context": response.web_context}


def should_continue(state: AgentState):
    """Determine whether to continue or not."""
    messages = state["messages"]
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
