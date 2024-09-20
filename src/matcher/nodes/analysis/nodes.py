from datetime import datetime

from langchain import hub
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from matcher.nodes.analysis.state import AnalysisMainState, AnalysisOutputState
from matcher.nodes.analysis.tools import ScoredCriterion, get_tools
from matcher.state import MainGraphState


def init_agent(state: AnalysisMainState) -> AnalysisMainState:
    hub_prompt = hub.pull("analysis-react")
    chat_prompt = ChatPromptTemplate.from_messages(hub_prompt.messages)
    formatted_messages = chat_prompt.format_messages(
        criterion_id=state.criterion_id,
        criterion_description=state.criterion_description,
        criterion_context=state.criterion_context,
        current_date=datetime.now().strftime("%Y-%m-%d"),
    )

    return {"messages": formatted_messages}


# Define the function that calls the model
def call_model(state: AnalysisMainState) -> AnalysisMainState:
    model_with_response_tool = ChatOpenAI(
        model="gpt-4o-2024-08-06", temperature=0
    ).bind_tools(get_tools(), parallel_tool_calls=False)

    response = model_with_response_tool.invoke(state.messages)
    return {"messages": [response]}


# Define the function that responds to the user
def respond(state: AnalysisOutputState) -> MainGraphState:
    response = ScoredCriterion(**state.messages[-1].tool_calls[0]["args"])
    # We return the final answer
    return {"scored_criterion": [response]}


# Define the function that determines whether to continue or not
def should_continue(state: AnalysisMainState) -> AnalysisMainState:
    messages = state.messages
    last_message = messages[-1]
    # If there is only one tool call and it is the response tool call we respond to the user
    if (
        len(last_message.tool_calls) == 1
        and last_message.tool_calls[0]["name"] == "ScoredCriterion"
    ):
        return "respond"
    # Otherwise we will use the tool node again
    else:
        return "continue"
