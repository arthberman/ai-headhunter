from typing import Literal, cast

from langchain import hub
from langchain_core.runnables import RunnableLambda
from langgraph.types import Command, interrupt

from feeder.utils.init_model import init_model
from src.feeder.models.location import LocationData
from src.feeder.state import OverallState

PROMPT_NAME = "get_relevant_locations_for_search_prompt"


async def get_relevant_location(
    state: OverallState,
) -> Command[Literal["process_in_job_titles_subgraph"]]:
    """Get the relevant location for the job offer description.

    Args:
        state: The overall state containing the job offer description and query memory.

    Returns:
        A dictionary containing the relevant location under the 'location' key.
    """
    if not state.job_offer_description or not state.job_offer_description.location:
        raise ValueError("No job offer description or location provided.")

    # state.job_offer_description.location contains format like "Paris, France"
    # we need to extract the city
    city = state.job_offer_description.location.split(",")[0]

    output = LocationData.model_validate(
        interrupt(
            {
                "action": "get_search_recruiter_location",
                "location": city,
            }
        )
    )

    llm = init_model("openai/o3-mini", temperature=0.0)
    structured_llm = llm.with_structured_output(LocationData)
    prompt = hub.pull(PROMPT_NAME)
    chain = cast(RunnableLambda, prompt | structured_llm)

    res = cast(
        LocationData,
        await chain.ainvoke(
            {
                "api_out_locations": output,
                "reference_job_location": state.job_offer_description.location,
            },
        ),
    )

    return Command(
        update={"locations": res.model_dump()},
        goto="process_in_job_titles_subgraph",
    )
