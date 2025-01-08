import asyncio
from typing import cast

from langchain_core.runnables import RunnableConfig
from pydantic import BaseModel, Field

from setup.configuration import Configuration
from setup.state import BaseResource, ResourceType, ScorecardGraphState
from utils import get_prompt, init_model


class CleanResource(BaseModel):
    """Clean resource."""

    content: str = Field(description="The cleaned content of the resource")


async def node_clean_resource(
    state: ScorecardGraphState, *, config: RunnableConfig
) -> ScorecardGraphState:
    """Clean resource content."""
    configuration = Configuration.from_runnable_config(config)
    raw_model = init_model("openai/gpt-4o-mini")
    prompt = get_prompt("clean-resource")
    chain = prompt | raw_model

    # Create async tasks for each resource
    async def clean_single_resource(resource: BaseResource) -> BaseResource:
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
        # Create a new resource with updated content, preserving all other fields
        updated_resource = resource.model_copy()
        updated_resource.content = cleaned.content
        return updated_resource

    # Run all cleaning tasks in parallel
    tasks = [
        clean_single_resource(resource)
        for resource in state.resources
        if (
            resource.content_type == ResourceType.URL
            or resource.content_type == ResourceType.PDF
        )
    ]
    cleaned_resources = await asyncio.gather(*tasks)

    # Return updated state with cleaned resources
    return {"cleaned_resources": cleaned_resources}
