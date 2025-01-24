from datetime import datetime
from typing import cast

from langchain_core.messages import AIMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableConfig, RunnableLambda
from langgraph.errors import GraphInterrupt
from langgraph.store.base import BaseStore, PutOp

from matcher.configuration import Configuration
from matcher.state import MainGraphState
from matcher.sub_graph.criterion_matcher.dynamic_prompt import (
    prepare_evaluation_steps,
    prepare_scoring_instructions,
)
from matcher.sub_graph.criterion_matcher.models import CotQuestions
from matcher.sub_graph.criterion_matcher.state import AnalysisMainState
from matcher.sub_graph.criterion_matcher.tools import ScoredCriterion, get_tools
from utils import clean_message, get_prompt, init_model


async def init_agent(
    state: AnalysisMainState, *, config: RunnableConfig, store: BaseStore
) -> AnalysisMainState:
    """Initialize the agent with the provided state."""
    # Load configuration from the provided RunnableConfig
    configuration = Configuration.from_runnable_config(config)

    namespace = ("scorecard", "criterion", str(state.criterion.id))
    key = "cot_questions"
    stored_questions = await store.aget(namespace, key)

    cot_questions = None
    op = None
    if stored_questions:
        cot_questions = CotQuestions(**stored_questions.value)
    else:
        prompt = get_prompt("analysis-cot-questions")
        raw_model = init_model(configuration.matcher_model)
        model = raw_model.with_structured_output(CotQuestions)

        # Create the chain
        chain = cast(RunnableLambda, prompt | model)

        cot_questions = cast(
            CotQuestions,
            await chain.ainvoke(
                {
                    "description": state.criterion.description,
                    "priority": state.criterion.priority.value,
                    "context": state.criterion.context,
                    "system_time": datetime.now().strftime("%B %d, %Y (%Y-%m-%-d)"),
                    "output_language": configuration.output_language,
                }
            ),
        )
        # Store the cot questions
        op = PutOp(namespace, key, cot_questions.model_dump(mode="json"), index=False)

    hub_prompt = get_prompt("score-analysis-criterion")
    chat_prompt = ChatPromptTemplate(hub_prompt.messages)

    instructions = prepare_scoring_instructions(state.criterion)
    evaluation_steps = prepare_evaluation_steps(cot_questions, instructions)

    formatted_messages = await chat_prompt.aformat_messages(
        id=state.criterion.id,
        description=state.criterion.description,
        priority=state.criterion.priority.value,
        category=state.criterion.category.value,
        scoring_distribution=state.criterion.scoring_distribution.value,
        context=state.criterion.context,
        evaluation_steps=evaluation_steps,
        output_language=configuration.output_language,
        system_time=datetime.now().strftime("%B %d, %Y (%Y-%m-%-d)"),
    )

    return {
        "messages": formatted_messages,
        "batch_store_ops": [op] if op else [],
    }


async def call_model(
    state: AnalysisMainState, *, config: RunnableConfig, store: BaseStore
) -> AnalysisMainState:
    """Call the model with the provided state and configuration."""
    # Load configuration from the provided RunnableConfig
    configuration = Configuration.from_runnable_config(config)

    # Initialize the raw model with the provided configuration and bind the tools
    raw_model = init_model(configuration.matcher_model)

    response = None
    op = None
    if state.loop_step == configuration.matcher_max_loops:
        message_content = """You exceeded the maximum number of iterations.
        You must respond to the user by calling the `ScoredCriterion` tool now."""
        messages = ChatPromptTemplate(
            [
                *state.messages,
                ("system", "{message_content}"),
            ]
        )
        # Bind the tools to the model
        model = raw_model.bind_tools([ScoredCriterion], tool_choice="ScoredCriterion")
        response = await model.ainvoke(
            await messages.ainvoke({"message_content": message_content})
        )
    else:
        if state.loop_step == 0:
            # First iteration, push pre tool call result directly to the model
            namespace = ("scorecard", "criterion", str(state.criterion.id))
            key = "init_tool_calls"
            stored_calls = await store.aget(namespace, key)

            if not stored_calls:
                # Bind the tools to the model
                model = raw_model.bind_tools(get_tools(), tool_choice="any")
                # Call the model with the provided state
                response = await model.ainvoke(state.messages)

                # Check if response is a tool call
                if (
                    getattr(response, "tool_calls", None)
                    and len(response.tool_calls) > 0
                ):
                    # Store the last message (AI Message with tool calls)
                    last_message = AIMessage(**clean_message(response).model_dump())
                    op = PutOp(
                        namespace,
                        key,
                        last_message.model_dump(mode="json"),
                        index=False,
                    )
            else:
                # Put the last message into the response
                response = AIMessage(**stored_calls.value)
        else:
            # Bind the tools to the model
            model = raw_model.bind_tools(get_tools(), tool_choice="any")
            # Call the model with the provided state
            response = await model.ainvoke(state.messages)

    return {
        "messages": [response],
        "loop_step": 1,  # Add 1 to the step count
        "batch_store_ops": [op] if op else [],
    }


async def respond(state: AnalysisMainState) -> MainGraphState:
    """Respond to the user with the scored criterion."""
    response = ScoredCriterion(**state.messages[-1].tool_calls[0]["args"])
    response.id = state.criterion.id  # prevent id mismatch
    # We return the final answer
    return {"scored_criterion": [response]}


def should_continue(
    state: AnalysisMainState, config: RunnableConfig
) -> AnalysisMainState:
    """Determine whether to continue or not."""
    # Load configuration from the provided RunnableConfig
    configuration = Configuration.from_runnable_config(config)

    messages = state.messages
    last_message = messages[-1]

    # If there is only one tool call and it is the response tool call we respond to the user
    if (
        getattr(last_message, "tool_calls", None)
        and len(last_message.tool_calls) == 1
        and last_message.tool_calls[0]["name"] == "ScoredCriterion"
    ):
        return "respond"
    # Check if the loop step exceeds the maximum number of loops
    elif state.loop_step >= configuration.matcher_max_loops + 1:
        raise GraphInterrupt("Graph exceeded maximum number of loops.")
    # Otherwise we will use the tool node again
    else:
        return "continue"
