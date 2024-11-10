"""Define the shared values."""

from pydantic import BaseModel, Field


class State(BaseModel):
    """Main graph state."""

    namespace: tuple[str, ...] = Field(
        ..., description="The namespace for the stored element."
    )
    key: str = Field(..., description="The key for the stored element.")

    information: str = Field(..., description="The information to store.")


class ProcessorState(State):
    """Extractor state."""

    function_name: str = Field(description="Name of the function being processed")


__all__ = [
    "State",
    "ProcessorState",
]
