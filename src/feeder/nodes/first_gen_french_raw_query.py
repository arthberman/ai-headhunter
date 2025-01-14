from typing import cast

from langchain import hub
from langchain_core.runnables import RunnableLambda

from feeder.models.raw_query import RawQuery
from feeder.utils.init_model import init_model
from feeder.state import OverallState


def first_gen_french_raw_query(state: OverallState) -> OverallState:
    """ "Generates the french version of the raw query."""
    llm = init_model("bedrock_converse/us.anthropic.claude-3-5-sonnet-20241022-v2:0")
    structured_llm = llm.with_structured_output(RawQuery)

    prompt = hub.pull("first_gen_french_json_object_prompt")
    chain = cast(RunnableLambda, prompt | structured_llm)
    french_json_object = cast(
        RawQuery,
        chain.invoke(
            {
                "job_offer_description": state.job_offer_description,
            }
        ),
    )
    json_object = state.json_object
    json_object.include = list(set(json_object.include + french_json_object.include))
    json_object.exclude = list(set(json_object.exclude + french_json_object.exclude))
    json_object.keywords = list(set(json_object.keywords + french_json_object.keywords))

    state.json_object = json_object
    return state
