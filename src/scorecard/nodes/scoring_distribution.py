from typing import Optional, cast

from utils import get_hub_prompt
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableConfig
from pydantic import model_validator
from trustcall import create_extractor

from scorecard.configuration import Configuration
from scorecard.models.scorecard import Scorecard
from scorecard.state import ScorecardGraphState
from utils import init_model


class ScorecardWithScoringDistributionValidation(Scorecard):
    """Scorecard with scoring distribution validation."""

    @model_validator(mode="after")
    def validate_scoring_distribution(
        self,
    ) -> "ScorecardWithScoringDistributionValidation":
        """Validate the scoring distribution."""
        for criterion in self.criteria:
            if criterion.scoring_distribution is None:
                raise ValueError("Scoring distribution for criterion must be provided.")
        return self


def node_scoring_distribution(
    state: ScorecardGraphState, *, config: Optional[RunnableConfig] = None
) -> ScorecardGraphState:
    """Generate scoring distribution for the scorecard criteria without existing distributions."""
    configuration = Configuration.from_runnable_config(config)

    prompt = get_hub_prompt("generate-scorecard-scoring-distribution")

    chat_prompt = ChatPromptTemplate.from_messages(prompt.messages)

    formatted_messages = chat_prompt.format_messages(
        raw_job_posting=state.raw_job_posting,
        web_context=state.web_context,
        human_context=state.human_context,
    )

    raw_model = init_model(configuration.structure_model)

    extractor = create_extractor(
        raw_model,
        tools=[ScorecardWithScoringDistributionValidation],
        tool_choice="ScorecardWithScoringDistributionValidation",
    )

    res = cast(
        ScorecardWithScoringDistributionValidation,
        extractor.invoke(
            {
                "messages": formatted_messages,
                "existing": {
                    "ScorecardWithScoringDistributionValidation": state.scorecard.model_dump()
                },
            }
        )["responses"][0],
    )

    return {"scorecard": cast(Scorecard, res)}
