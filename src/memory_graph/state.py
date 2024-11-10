"""Define the shared values."""

from pydantic import BaseModel, Field


class State(BaseModel):
    """Main graph state."""

    namespace: tuple[str, ...] = Field(
        ..., description="The namespace for the stored element."
    )
    key: str = Field(..., description="The key for the stored element.")

    information: str = Field(..., description="The information to store.")

    function_name: str = Field(..., description="The function name for the stored element.")


class ProcessorState(State):
    """Extractor state."""
    pass


__all__ = [
    "State",
    "ProcessorState",
]
