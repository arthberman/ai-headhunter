from typing import cast

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableConfig
from trustcall import create_extractor

from setup.configuration import Configuration
from setup.models.question import ListQuestions
from setup.state import ScorecardGraphState
from utils import get_prompt, init_model


def node_questions(
    state: ScorecardGraphState, *, config: RunnableConfig
) -> ScorecardGraphState:
    """Generate questions for the scorecard criteria."""
    # Load configuration from the provided RunnableConfig
    configuration = Configuration.from_runnable_config(config)

    prompt = get_prompt("generate-scorecard-questions")
    chat_prompt = ChatPromptTemplate.from_messages(prompt.messages)

    formatted_messages = chat_prompt.format_messages(
        resources=state.get_all_resources_without_feedback(as_dict=True),
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

    return {"generated_questions": res}
