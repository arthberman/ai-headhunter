from typing import Optional, cast

from langchain import hub
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableConfig
from trustcall import create_extractor

from scorecard.configuration import Configuration
from scorecard.models.scorecard import Scorecard
from scorecard.state import ScorecardGraphState
from utils import init_model


def node_judge_scorecard_structure(
    state: ScorecardGraphState, *, config: Optional[RunnableConfig] = None
) -> ScorecardGraphState:
    """Judge and potentially modify the scorecard structure."""
    configuration = Configuration.from_runnable_config(config)
    raw_model = init_model(configuration.structure_model)
    extractor = create_extractor(raw_model, tools=[Scorecard])

    prompt = hub.pull("judge-scorecard-structure")
    chat_prompt = ChatPromptTemplate.from_messages(prompt.messages)

    formatted_messages = chat_prompt.format_messages()

    res = cast(
        Scorecard,
        extractor.invoke(
            {
                "messages": formatted_messages,
                "existing": {"Scorecard": state.scorecard.model_dump()},
            }
        )["responses"][0],
    )

    return {"scorecard": res}
