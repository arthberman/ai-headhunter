from typing import cast

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableConfig
from langgraph.types import StreamWriter
from trustcall import create_extractor

from setup.configuration import Configuration
from setup.models.question import ListQuestions
from setup.state import (
    ScorecardGraphState,
    StreamCustomEvents,
    StreamCustomEventsStatus,
)
from utils import get_prompt, init_model


def node_questions(
    state: ScorecardGraphState, writer: StreamWriter, *, config: RunnableConfig
) -> ScorecardGraphState:
    """Generate questions for the scorecard criteria."""
    # Send stream event
    writer(
        {
            "event_name": StreamCustomEvents.GENERATE_QUESTIONS,
            "status": StreamCustomEventsStatus.STARTED,
        }
    )
    # Load configuration from the provided RunnableConfig
    configuration = Configuration.from_runnable_config(config)

    prompt = get_prompt("generate-scorecard-questions")
    chat_prompt = ChatPromptTemplate.from_messages(prompt.messages)

    formatted_messages = chat_prompt.format_messages(
        resources=state.resources,
    )

    raw_model = init_model(configuration.structure_model)

    extractor = create_extractor(
        raw_model, tools=[ListQuestions], tool_choice="ListQuestions"
    )

    res = cast(
        ListQuestions,
        extractor.invoke(
            {
                "messages": formatted_messages,
            }
        )["responses"][0],
    )

    # Put all final answers to None
    for question in res.questions:
        question.final_answer = None

    # Send stream event
    writer(
        {
            "event_name": StreamCustomEvents.GENERATE_QUESTIONS,
            "status": StreamCustomEventsStatus.COMPLETED,
        }
    )

    return {"questions": res}
