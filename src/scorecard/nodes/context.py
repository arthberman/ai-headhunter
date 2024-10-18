from typing import Optional, cast

from langchain import hub
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableConfig
from pydantic import model_validator
from trustcall import create_extractor

from scorecard.configuration import Configuration
from scorecard.models.scorecard import Scorecard
from scorecard.state import ScorecardGraphState
from utils import init_model


class ScorecardWithContextValidation(Scorecard):
    """Scorecard with context validation."""

    @model_validator(mode="after")
    def validate_context_length(self) -> "ScorecardWithContextValidation":
        """Validate the context length."""
        for criterion in self.criteria:
            if criterion.context is None or len(criterion.context) < 80:
                raise ValueError(
                    "Context is mandatory for all criteria and should be 200 characters long."
                )
        return self


def node_context(
    state: ScorecardGraphState, *, config: Optional[RunnableConfig] = None
) -> ScorecardGraphState:
    """Generate context for the scorecard criteria without existing context."""
    # Load configuration from the provided RunnableConfig
    configuration = Configuration.from_runnable_config(config)

    prompt = hub.pull("generate-scorecard-context")
    chat_prompt = ChatPromptTemplate.from_messages(prompt.messages)

    formatted_messages = chat_prompt.format_messages(
        raw_job_posting=state.raw_job_posting,
        web_context=state.web_context,
        human_context=state.human_context,
    )

    raw_model = init_model(configuration.structure_model)

    extractor = create_extractor(
        raw_model,
        tools=[ScorecardWithContextValidation],
        tool_choice="ScorecardWithContextValidation",
    )

    res = cast(
        ScorecardWithContextValidation,
        extractor.invoke(
            {
                "messages": formatted_messages,
                "existing": {
                    "ScorecardWithContextValidation": state.scorecard.model_dump()
                },
            }
        )["responses"][0],
    )

    return {"scorecard": cast(Scorecard, res)}
