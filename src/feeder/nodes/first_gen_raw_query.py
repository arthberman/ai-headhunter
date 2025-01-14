from typing import cast

from langchain import hub
from langchain_core.runnables import RunnableLambda

from feeder.models.raw_query import RawQuery
from feeder.utils.init_model import init_model
from feeder.state import OverallState
from feeder.subgraph.location.state import LocationSubGraphInputState


def first_gen_raw_query(state: OverallState) -> LocationSubGraphInputState:
    """Generate a first generation raw query."""
    llm = init_model("bedrock_converse/us.anthropic.claude-3-5-sonnet-20241022-v2:0")
    structured_llm = llm.with_structured_output(RawQuery)
    prompt = hub.pull("first_gen_json_object_prompt")
    chain = cast(RunnableLambda, prompt | structured_llm)
    res = cast(
        RawQuery,
        chain.invoke(
            {
                "job_offer_description": state.job_offer_description,
                "query_memory": state.query_memory
                if state.query_memory is not None
                else "",
            }
        ),
    )
    # Reset query-related state since we're starting fresh
    return {
        "json_object": res,
        "current_query_index": 0,
        "query_results": None,
    }
