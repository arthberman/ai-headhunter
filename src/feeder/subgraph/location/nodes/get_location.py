from typing import cast

from langchain import hub
from langchain_core.runnables import RunnableLambda

from feeder.utils.init_model import init_model
from feeder.models.location import Location
from feeder.subgraph.location.state import LocationSubGraphState


def get_location(state: LocationSubGraphState) -> LocationSubGraphState:
    """Extract location information from job offer description."""
    llm = init_model("bedrock_converse/us.anthropic.claude-3-5-sonnet-20241022-v2:0")
    structured_llm = llm.with_structured_output(Location)

    prompt = hub.pull("get_location_prompt")
    chain = cast(RunnableLambda, prompt | structured_llm)
    res = cast(
        Location,
        chain.invoke(
            {"job_offer": state.job_offer_description},
        ),
    )
    return {"job_location": res.name}
