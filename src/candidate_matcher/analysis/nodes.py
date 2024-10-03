from datetime import datetime
from typing import Optional, cast

from langchain import hub
from langchain_core.messages import HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable, RunnableConfig

from candidate_matcher.analysis.state import AnalysisMainState
from candidate_matcher.analysis.tools import ScoredCriterion, get_tools
from candidate_matcher.configuration import Configuration
from candidate_matcher.state import MainGraphState
from candidate_matcher.utils import init_model, log_cancelled_error


@log_cancelled_error
def init_agent(
    state: AnalysisMainState, *, config: Optional[RunnableConfig] = None
) -> AnalysisMainState:
    """Initialize the agent with the provided state."""
    # Load configuration from the provided RunnableConfig
    configuration = Configuration.from_runnable_config(config)

    hub_prompt = hub.pull("score-analysis-criterion")
    chat_prompt = ChatPromptTemplate.from_messages(hub_prompt.messages)
    formatted_messages = chat_prompt.format_messages(
        id=state.criterion.id,
        description=state.criterion.description,
        context=state.criterion.context,
        scoring_distribution=state.criterion.scoring_distribution,
        current_date=datetime.now().strftime("%Y-%m-%d"),
    )

    # if it's a bedrock_converse model
    if configuration.analysis_model.startswith("bedrock_converse"):
        # replace the first system message with a user message to fit Bedrock Converse API requirements
        formatted_messages[0] = HumanMessage(content=formatted_messages[0].content)

    return {"messages": formatted_messages}


# Define the function that calls the model
@log_cancelled_error
def call_model(
    state: AnalysisMainState, *, config: Optional[RunnableConfig] = None
) -> AnalysisMainState:
    """Call the model with the provided state and configuration."""
    # Load configuration from the provided RunnableConfig
    configuration = Configuration.from_runnable_config(config)

    # Initialize the raw model with the provided configuration and bind the tools
    raw_model = init_model(configuration.analysis_model)

    # Bind the tools to the model
    model = raw_model.bind_tools(get_tools(), tool_choice="any")

    # Call the model with the provided state
    response = model.invoke(state.messages)

    return {
        "messages": [response],
        # Add 1 to the step count
        "loop_step": 1,
    }


# Define the function that responds to the user
@log_cancelled_error
def respond(state: AnalysisMainState) -> MainGraphState:
    """Respond to the user with the scored criterion."""
    response = ScoredCriterion(**state.messages[-1].tool_calls[0]["args"])
    # We return the final answer
    return {"scored_criterion": [response]}


@log_cancelled_error
def respond_exceed_max_loops(
    state: AnalysisMainState, *, config: Optional[RunnableConfig] = None
) -> MainGraphState:
    """Respond to the user when the maximum number of loops is exceeded."""
    # Load configuration from the provided RunnableConfig
    configuration = Configuration.from_runnable_config(config)

    # Initialize the raw model with the provided configuration
    raw_model = init_model(configuration.analysis_model)

    # Create a structured output model for the JobPosting
    model = raw_model.with_structured_output(ScoredCriterion)

    hub_prompt = hub.pull("score-analysis-respond")

    chain = cast(Runnable, model | hub_prompt)

    formatted_messages = [
        {
            "type": msg.__class__.__name__,
            "content": msg.content,
            "additional_kwargs": msg.additional_kwargs,
        }
        for msg in state.messages
    ]

    output = cast(ScoredCriterion, chain.invoke({"messages": formatted_messages}))

    # We return the final answer
    return {"scored_criterion": [output]}


# Define the function that determines whether to continue or not
@log_cancelled_error
def should_continue(
    state: AnalysisMainState, config: RunnableConfig
) -> AnalysisMainState:
    """Determine whether to continue or not."""
    # Load configuration from the provided RunnableConfig
    configuration = Configuration.from_runnable_config(config)

    # Check if the loop step exceeds the maximum number of loops
    if state.loop_step >= configuration.analysis_max_loops:
        return "respond_exceed_max_loops"

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
