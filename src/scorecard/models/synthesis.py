from pydantic import BaseModel, Field


class Synthesis(BaseModel):
    """Synthesis of the scorecard in one paragraph."""

    description: str = Field(
        ..., description="Synthesis of the scorecard in one paragraph."
    )
