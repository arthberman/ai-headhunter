from typing import Optional, cast

from langchain import hub
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableConfig
from trustcall import create_extractor

from scorecard.configuration import Configuration
from scorecard.models.scorecard import Scorecard
from scorecard.state import ScorecardGraphState
from utils import init_model

prompt_iterative_instruction = """
You are in the UPDATE stage of the scorecard design process.
You are given a job scorecard to update based on the human feedback.
Do not suggest changes that aren't directly addressed in the human feedback.

When updating the scorecard, you must only follow the human feedback provided :
<human_feedback>
{human_feedback}
</human_feedback>
"""


def node_scorecard_structure(
    state: ScorecardGraphState, *, config: Optional[RunnableConfig] = None
) -> ScorecardGraphState:
    """Generate a scorecard structure based on the human feedback."""
    # Load configuration from the provided RunnableConfig
    configuration = Configuration.from_runnable_config(config)
    # Initialize the chat model with the provided configuration
    raw_model = init_model(configuration.structure_model)

    extractor = create_extractor(raw_model, tools=[Scorecard])

    hub_prompt = hub.pull("generate-scorecard-structure")
    chat_prompt = ChatPromptTemplate.from_messages(hub_prompt.messages)

    formatted_messages = chat_prompt.format_messages(
        raw_job_posting=state.raw_job_posting,
        web_context=state.web_context,
        human_context=state.human_context,
        iterative_instruction=(
            prompt_iterative_instruction.format(human_feedback=state.human_feedback)
            if state.scorecard and state.human_feedback
            else ""
        ),
    )

    res = cast(
        Scorecard,
        extractor.invoke(
            {
                "messages": formatted_messages,
                "existing": (
                    {"Scorecard": state.scorecard.model_dump()}
                    if state.scorecard
                    else None
                ),
            }
        )["responses"][0],
    )

    return {
        "scorecard": res,
        "human_context": (state.human_context or []) + (state.human_feedback or []),
        "human_feedback": [],
    }
