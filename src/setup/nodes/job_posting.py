from typing import cast

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableConfig
from langgraph.types import StreamWriter
from trustcall import create_extractor

from setup.configuration import Configuration
from setup.models.job_posting import JobPosting
from setup.state import (
    ScorecardGraphState,
    StreamCustomEvents,
    StreamCustomEventsStatus,
)
from utils import get_prompt, init_model


def node_job_posting(
    state: ScorecardGraphState, writer: StreamWriter, *, config: RunnableConfig
) -> ScorecardGraphState:
    """Generate job posting for the scorecard criteria."""
    # Send stream event
    writer(
        {
            "event_name": StreamCustomEvents.GENERATE_JOB_POSTING,
            "status": StreamCustomEventsStatus.IN_PROGRESS,
        }
    )
    # Load configuration from the provided RunnableConfig
    configuration = Configuration.from_runnable_config(config)
    # Initialize the chat model with the provided configuration
    raw_model = init_model(configuration.structure_model)
    # Create an extractor for the JobPosting
    extractor = create_extractor(
        raw_model, tools=[JobPosting], tool_choice="JobPosting"
    )
    # Pull the prompt from the hub
    prompt = get_prompt("generate-scorecard-job-posting")
    chat_prompt = ChatPromptTemplate.from_messages(prompt.messages)
    formatted_messages = chat_prompt.format_messages(
        resources=state.resources,
    )
    # Invoke the extractor with the formatted messages
    res = cast(
        JobPosting,
        extractor.invoke(
            {
                "messages": formatted_messages,
            }
        )["responses"][0],
    )

    # Send stream event
    writer(
        {
            "event_name": StreamCustomEvents.GENERATE_JOB_POSTING,
            "status": StreamCustomEventsStatus.COMPLETED,
        }
    )
    return {"job_posting": res}
