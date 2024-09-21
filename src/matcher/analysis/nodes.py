from datetime import datetime
from typing import Optional

from langchain import hub
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from matcher.analysis.state import AnalysisMainState, AnalysisOutputState
from matcher.analysis.tools import ScoredCriterion, get_tools
from matcher.state import MainGraphState
from src.matcher.configuration import Configuration
from langchain_core.runnables import RunnableConfig

from src.matcher.utils import init_model
from langchain.chat_models import init_chat_model


def init_agent(state: AnalysisMainState) -> AnalysisMainState:
    """Initialize the agent with the provided state."""

    hub_prompt = hub.pull("analysis-react")
    chat_prompt = ChatPromptTemplate.from_messages(hub_prompt.messages)
    formatted_messages = chat_prompt.format_messages(
        id=state.criterion.id,
        description=state.criterion.description,
        context=state.criterion.context,
        scoring_distribution=state.criterion.scoring_distribution,
        distribution_params=state.criterion.distribution_params,
        current_date=datetime.now().strftime("%Y-%m-%d"),
    )

    return {"messages": formatted_messages}


# Define the function that calls the model
def call_model(
    state: AnalysisMainState, *, config: Optional[RunnableConfig] = None
) -> AnalysisMainState:
    """Call the model with the provided state and configuration."""

    # Load configuration from the provided RunnableConfig
    configuration = Configuration.from_runnable_config(config)

    # Check if the loop step is greater than the maximum number of loops
    if state.loop_step == configuration.analysis_max_loops:
        return {
            "messages": [
                "You exceeded the maximum number of loops. You must respond to the user by calling the ScoredCriterion tool."
            ]
        }

    # Initialize the raw model with the provided configuration and bind the tools
    raw_model = init_model(configuration.analysis_model)

    # Bind the tools to the model
    model = raw_model.bind_tools(get_tools(), parallel_tool_calls=False)

    # Call the model with the provided state
    response = model.invoke(state.messages)

    return {
        "messages": [response],
        # Add 1 to the step count
        "loop_step": 1,
    }


# Define the function that responds to the user
def respond(state: AnalysisOutputState) -> MainGraphState:
    """Respond to the user with the scored criterion."""

    response = ScoredCriterion(**state.messages[-1].tool_calls[0]["args"])
    # We return the final answer
    return {"scored_criterion": [response]}


# Define the function that determines whether to continue or not
def should_continue(
    state: AnalysisMainState, config: RunnableConfig
) -> AnalysisMainState:
    """Determine whether to continue or not."""

    # Load configuration from the provided RunnableConfig
    configuration = Configuration.from_runnable_config(config)

    # Check if the loop step is greater than the maximum number of loops + 2
    if state.loop_step >= configuration.analysis_max_loops + 2:
        return "__end__"

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
