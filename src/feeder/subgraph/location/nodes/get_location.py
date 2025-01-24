from logging import getLogger
from typing import cast

from langchain import hub
from langchain_core.runnables import RunnableLambda

from feeder.utils.init_model import init_model
from src.feeder.models.location import Location
from src.feeder.subgraph.location.state import LocationSubGraphState

logger = getLogger(__name__)


async def get_location(state: LocationSubGraphState) -> LocationSubGraphState:
    """Extract location information from job offer description.

    LLM Processing:
    - Uses structured output to enforce location format
    - Handles various location format (city, country, region)
    """
    llm = init_model("bedrock_converse/us.anthropic.claude-3-5-sonnet-20241022-v2:0")
    structured_llm = llm.with_structured_output(Location)

    prompt = hub.pull("get_location_prompt")
    chain = cast(RunnableLambda, prompt | structured_llm)
    res = cast(
        Location,
        await chain.ainvoke(
            {"job_offer": state.job_offer_description},
        ),
    )
    logger.info(f"res.name: {res.name}")
    return {
        "job_location": res.name
    }  # res.name because job_location is defined as a string in the state
