"""Define the models for the scorecard synthesis."""

from pydantic import BaseModel


class Synthesis(BaseModel):
    description: str
