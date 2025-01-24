from enum import Enum
from typing import List

from pydantic import BaseModel, Field


class CompanyMaturityStage(str, Enum):
    """The maturity stage of the company."""

    SEED = "seed"  # Initial stage, product development
    EARLY = "early"  # Product launched, seeking product-market fit
    GROWTH = "growth"  # Proven model, focusing on scaling
    EXPANSION = "expansion"  # Multiple markets/products, rapid scaling
    MATURE = "mature"  # Established market position, stable growth
    DECLINE = "decline"  # Decreasing market share/growth


class CompanySize(str, Enum):
    """The size of the company."""

    MICRO = "micro"  # <10 employees, <€2M revenue
    SMALL = "small"  # <50 employees, <€10M revenue
    MEDIUM = "medium"  # <250 employees, <€50M revenue
    LARGE = "large"  # >250 employees, >€50M revenue
    BIG_CORPORATION = "big_corporation"  # >5000 employees or >€1B revenue


class CompanyStatus(str, Enum):
    """The legal/ownership status of the company."""

    PRIVATE = "private"
    PUBLIC = "public"
    SUBSIDIARY = "subsidiary"
    STATE_OWNED = "state_owned"
    COOPERATIVE = "cooperative"


class CompanyInfo(BaseModel):
    """Information about a company learned from employee LinkedIn profiles."""

    company_name: str = Field(description="Official name of the company")
    founding_year: int | None = Field(None, description="Year the company was founded")
    founder_names: List[str] | None = Field(
        None, description="Names of the founding team members"
    )
    product_description: str | None = Field(
        None,
        description="Comprehensive description of the company's products or services, including key features, target market, competitive advantages, and technical specifications where applicable",
    )
    funding_summary: str | None = Field(
        None,
        description="Detailed funding history including all investment rounds, investors, amounts raised, valuations, and significant financial milestones or strategic investments",
    )
    maturity_stage: CompanyMaturityStage | None = Field(
        None,
        description="Current maturity stage in the company lifecycle",
        examples=["growth"],
    )
    company_size: CompanySize | None = Field(
        None,
        description="Size classification based on employees and revenue",
        examples=["medium"],
        json_schema_extra={
            "additionalProperties": {
                "micro": "< 10 employees, < €2M revenue",
                "small": "< 50 employees, < €10M revenue",
                "medium": "< 250 employees, < €50M revenue",
                "large": "> 250 employees, > €50M revenue",
                "big_corporation": "> 5000 employees or > €1B revenue",
            }
        },
    )
    company_status: CompanyStatus | None = Field(
        None, description="Legal/ownership status of the company", examples=["private"]
    )

    model_config = {
        "title": "CompanyInfo",
        "description": "Basic information about a company",
        "json_schema_extra": {"additionalProperties": False},
    }
