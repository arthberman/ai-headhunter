from typing import cast

from langchain_core.runnables import RunnableConfig
from pydantic import BaseModel, Field

from feedback.configuration import Configuration
from feedback.state import FeedbackClassifier, FeedbackGraphState
from utils import get_prompt, init_model


class Pattern(BaseModel):
    """A pattern from the feedback."""

    description: str = Field(..., description="A description of the pattern.")
    context: str = Field(
        ...,
        description="The situation or circumstance where this pattern may be relevant. "
        "Include any caveats or conditions that contextualize the pattern. "
        "Add any other relevant 'meta' details that help fully understand when and how to use this pattern.",
    )


async def node_pattern(
    state: FeedbackGraphState, *, config: RunnableConfig
) -> FeedbackGraphState:
    """Node to extract patterns from the feedback."""
    configuration = Configuration.from_runnable_config(config)

    prompt = get_prompt("feedback-classifier")
    raw_model = init_model(configuration.small_model)
    model = raw_model.with_structured_output(FeedbackClassifier)

    chain = prompt | model

    res = cast(
        Pattern,
        await chain.ainvoke({"feedback": state.feedback}),
    )

    return {"classifier": res.classifier}
