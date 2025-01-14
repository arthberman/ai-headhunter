import asyncio
from typing import cast

from langchain_core.runnables import RunnableConfig
from langgraph.types import StreamWriter
from pydantic import BaseModel, Field

from setup.configuration import Configuration
from setup.state import (
    BaseResource,
    ResourceType,
    ScorecardGraphState,
    StreamCustomEvents,
    StreamCustomEventsStatus,
)
from utils import get_prompt, init_model


class CleanResource(BaseModel):
    """Clean resource."""

    content: str = Field(description="The cleaned content of the resource")


async def node_clean_resource(
    state: ScorecardGraphState, writer: StreamWriter, *, config: RunnableConfig
) -> ScorecardGraphState:
    """Clean resource content."""
    # Send stream event
    writer(
        {
            "event_name": StreamCustomEvents.CLEAN_ALL_RESOURCES,
            "status": StreamCustomEventsStatus.STARTED,
        }
    )

    configuration = Configuration.from_runnable_config(config)
    raw_model = init_model(configuration.cleaning_model)
    prompt = get_prompt("clean-resource")
    chain = prompt | raw_model

    # Create async tasks for each resource
    async def clean_single_resource(resource: BaseResource) -> None:
        writer(
            {
                "event_name": StreamCustomEvents.CLEAN_RESOURCE,
                "status": StreamCustomEventsStatus.STARTED,
                "metadata": {"resource_id": resource.id},
            }
        )
        cleaned = cast(
            CleanResource,
            (
                await chain.ainvoke(
                    {
                        "content": resource.content,
                    }
                )
            ),
        )
        writer(
            {
                "event_name": StreamCustomEvents.CLEAN_RESOURCE,
                "status": StreamCustomEventsStatus.COMPLETED,
                "metadata": {"resource_id": resource.id},
            }
        )
        # Update the content of the original resource
        resource.content = cleaned.content

    # Run all cleaning tasks in parallel
    tasks = [
        clean_single_resource(resource)
        for resource in state.resources
        if (
            resource.content_type == ResourceType.URL
            or resource.content_type == ResourceType.PDF
        )
    ]
    await asyncio.gather(*tasks)

    # Send stream event
    writer(
        {
            "event_name": StreamCustomEvents.CLEAN_ALL_RESOURCES,
            "status": StreamCustomEventsStatus.COMPLETED,
        }
    )
    # Return updated state with the modified resources
    return {"resources": state.resources}
