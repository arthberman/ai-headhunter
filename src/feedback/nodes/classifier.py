from typing import cast

from langchain_core.runnables import RunnableConfig
from pydantic import BaseModel, Field

from feedback.configuration import Configuration
from feedback.state import FeedbackClassifier, FeedbackGraphState
from utils import get_prompt, init_model


class FeedbackClassifierOutput(BaseModel):
    """Output of the feedback classifier."""

    classifier: FeedbackClassifier = Field(...)


async def node_classifier(
    state: FeedbackGraphState, *, config: RunnableConfig
) -> FeedbackGraphState:
    """Node to classify feedback into different categories."""
    configuration = Configuration.from_runnable_config(config)

    prompt = get_prompt("feedback-classifier")
    raw_model = init_model(configuration.small_model)
    model = raw_model.with_structured_output(FeedbackClassifier)

    chain = prompt | model

    res = cast(
        FeedbackClassifierOutput,
        await chain.ainvoke({"feedback": state.feedback}),
    )

    return {"classifier": res.classifier}
