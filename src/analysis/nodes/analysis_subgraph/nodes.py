from datetime import datetime
from typing import Optional, cast

from langchain import hub
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableConfig, RunnableLambda

from analysis.full.state import MainGraphState
from analysis.iterative.configuration import Configuration
from analysis.nodes.analysis_subgraph.dynamic_prompt import (
    prepare_evaluation_steps,
    prepare_scoring_instructions,
)
from analysis.nodes.analysis_subgraph.models import CotQuestions
from analysis.nodes.analysis_subgraph.state import AnalysisMainState
from analysis.nodes.analysis_subgraph.tools import ScoredCriterion, get_tools
from utils import init_model


def init_agent(
    state: AnalysisMainState, *, config: Optional[RunnableConfig] = None
) -> AnalysisMainState:
    """Initialize the agent with the provided state."""
    # Load configuration from the provided RunnableConfig
    configuration = Configuration.from_runnable_config(config)

    prompt = hub.pull("analysis-cot-questions:development")
    raw_model = init_model(
        "bedrock_converse/us.anthropic.claude-3-5-sonnet-20241022-v2:0"
    )
    model = raw_model.with_structured_output(CotQuestions)

    # Create the chain
    chain = cast(RunnableLambda, prompt | model)

    cot_questions = cast(
        CotQuestions,
        chain.invoke(
            {
                "description": state.criterion.description,
                "importance_level": state.criterion.importance_level.value,
                "context": state.criterion.context,
            }
        ),
    )

    hub_prompt = hub.pull("score-analysis-criterion:development")
    chat_prompt = ChatPromptTemplate.from_messages(hub_prompt.messages)

    instructions = prepare_scoring_instructions(state.criterion)
    evaluation_steps = prepare_evaluation_steps(cot_questions, instructions)

    formatted_messages = chat_prompt.format_messages(
        id=state.criterion.id,
        description=state.criterion.description,
        importance_level=state.criterion.importance_level.value,
        type=state.criterion.type.value,
        scoring_distribution=state.criterion.scoring_distribution.value,
        context=state.criterion.context,
        evaluation_steps=evaluation_steps,
        system_time=datetime.now().isoformat(),
    )

    # if it's a bedrock_converse model
    if configuration.analysis_model.startswith("bedrock_converse"):
        # replace the first system message with a user message to fit Bedrock Converse API requirements
        formatted_messages[0] = HumanMessage(content=formatted_messages[0].content)

    return {"messages": formatted_messages}


# Define the function that calls the model
def call_model(
    state: AnalysisMainState, *, config: Optional[RunnableConfig] = None
) -> AnalysisMainState:
    """Call the model with the provided state and configuration."""
    # Load configuration from the provided RunnableConfig
    configuration = Configuration.from_runnable_config(config)

    # Check if the loop step is greater than the maximum number of loops
    if state.loop_step == configuration.analysis_max_loops - 1:
        return {
            "messages": [
                AIMessage(
                    content="You exceeded the maximum number of loops. You must respond to the user by calling the WebContext tool now."
                )
            ],
            "loop_step": 1,
        }

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


def respond(state: AnalysisMainState) -> MainGraphState:
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

    # Check if the loop step exceeds the maximum number of loops
    if state.loop_step >= configuration.analysis_max_loops + 3:
        return "__end__"

    messages = state.messages
    last_message = messages[-1]

    # If there is only one tool call and it is the response tool call we respond to the user
    if (
        last_message.tool_calls
        and len(last_message.tool_calls) == 1
        and last_message.tool_calls[0]["name"] == "ScoredCriterion"
    ):
        return "respond"
    # Otherwise we will use the tool node again
    else:
        return "continue"
