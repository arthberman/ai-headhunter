from typing import Optional, cast

from langchain import hub
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableConfig
from trustcall import create_extractor

from scorecard.configuration import Configuration
from scorecard.models.question import ListQuestions
from scorecard.state import ScorecardGraphState
from utils import init_model


def node_questions(
    state: ScorecardGraphState, *, config: Optional[RunnableConfig] = None
) -> ScorecardGraphState:
    """Generate questions for the scorecard criteria."""
    # Load configuration from the provided RunnableConfig
    configuration = Configuration.from_runnable_config(config)

    prompt = hub.pull("generate-scorecard-questions")
    chat_prompt = ChatPromptTemplate.from_messages(prompt.messages)

    formatted_messages = chat_prompt.format_messages(
        raw_job_posting=state.raw_job_posting,
        web_context=state.web_context,
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
                # "existing": {"ListQuestions": existing_questions.model_dump()},
            }
        )["responses"][0],
    )

    return {"generated_questions": res}
