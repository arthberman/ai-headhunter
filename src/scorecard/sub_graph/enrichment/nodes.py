from langchain_core.prompts import ChatPromptTemplate
from langchain import hub
from langchain_openai import ChatOpenAI
from langgraph.graph import END, MessagesState

from scorecard.sub_graph.enrichment.tools import GlobalContext, get_tools


# Define the AgentState
class AgentState(MessagesState):
    raw_job_posting: str
    global_context: GlobalContext


def init_agent(state: AgentState):
    hub_prompt = hub.pull("scorecard-enrichment-react-basic")

    chat_prompt = ChatPromptTemplate.from_messages(hub_prompt.messages)

    formatted_messages = chat_prompt.format_messages(
        raw_job_posting=state["raw_job_posting"]
    )

    return {"messages": formatted_messages}


# Define the function that calls the model
def call_model(state: AgentState):
    model_with_response_tool = ChatOpenAI(
        model="gpt-4o-mini", temperature=0
    ).bind_tools(get_tools(), tool_choice="any", parallel_tool_calls=False)

    response = model_with_response_tool.invoke(state["messages"])
    return {"messages": [response]}


# Define the function that responds to the user
def respond(state: AgentState):
    response = GlobalContext(**state["messages"][-1].tool_calls[0]["args"])
    # We return the final answer
    return {"global_context": response.global_context}


# Define the function that determines whether to continue or not
def should_continue(state: AgentState):
    messages = state["messages"]
    last_message = messages[-1]
    # If there is only one tool call and it is the response tool call we respond to the user
    if (
        len(last_message.tool_calls) == 1
        and last_message.tool_calls[0]["name"] == "GlobalContext"
    ):
        return "respond"
    # Otherwise we will use the tool node again
    else:
        return "continue"
