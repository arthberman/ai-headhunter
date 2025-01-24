from typing import cast

from langchain import hub
from langchain_core.runnables import RunnableLambda

from feeder.models.raw_query import RawQuery
from feeder.utils.init_model import init_model
from src.feeder.state import OverallState


async def first_gen_french_raw_query(state: OverallState) -> OverallState:
    """Generate the French version of the raw query and merge it with the existing query."""
    llm = init_model("bedrock_converse/us.anthropic.claude-3-5-sonnet-20241022-v2:0")
    structured_llm = llm.with_structured_output(RawQuery)

    prompt = hub.pull("first_gen_french_json_object_prompt")
    chain = cast(RunnableLambda, prompt | structured_llm)
    french_json_object = cast(
        RawQuery,
        await chain.ainvoke(
            {
                "job_offer_description": state.job_offer_description,
                "query_memory": state.query_memory
                if state.query_memory is not None
                else "",  # add query memory to the prompt only if it is exists (i.e. previous generations have been run)
            }
        ),
    )
    # merge the French elements of the query with the existing ones and deduplicate
    json_object = state.json_object
    json_object.in_job_titles = list(
        set(json_object.in_job_titles + french_json_object.in_job_titles)
    )
    json_object.not_in_job_titles = list(
        set(json_object.not_in_job_titles + french_json_object.not_in_job_titles)
    )
    json_object.keywords = list(set(json_object.keywords + french_json_object.keywords))

    state.json_object = json_object
    return state
