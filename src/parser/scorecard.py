from typing import List
from langchain import hub
from langchain.chat_models import init_chat_model
from langchain_core.pydantic_v1 import BaseModel, Field, validator

from matcher.models.job_posting import JobPosting
from matcher.models.scorecard import Scorecard


class CriterionEnrichment(BaseModel):
    guidelines: List[str] = Field(
        description=f"List of specific, actionable instructions for evaluating the criterion based on a candidate's resume or LinkedIn profile."
        "Each guideline should provide clear direction on what to look for in these documents, such as specific experiences, skills, achievements, prestige that indicate the candidate meets this criterion."
        # Guidelines should be designed to be easily applicable when reviewing written professional summaries, without requiring additional information beyond what's typically found in a resume or LinkedIn profile.
    )
    examples_positive: List[str] = Field(
        ...,
        description="List of examples that clearly meet or exceed the criterion, illustrating ideal candidate profiles",
    )

    examples_negative: List[str] = Field(
        ...,
        description="List of examples that do not meet the criterion, illustrating profiles that fall short of the requirement",
    )
    examples_borderline: List[str] = Field(
        ...,
        description="List of examples that partially meet the criterion, illustrating profiles that are on the edge of acceptability",
    )


def parse_scorecard(job_posting: JobPosting) -> Scorecard:
    model = init_chat_model(
        model="gpt-4o-2024-08-06",
        model_provider="openai",
        temperature=0,
    )
    structured_model = model.with_structured_output(Scorecard)
    prompt = hub.pull("parser-scorecard")

    chain = prompt | structured_model
    output: Scorecard = chain.invoke(job_posting)

    for criterion in output.mustHaveCriteria.criteria:
        enriched_criterion = enrich_criterion(criterion.description)
        criterion.guidelines = enriched_criterion.guidelines
        criterion.examples_positive = enriched_criterion.examples_positive
        criterion.examples_negative = enriched_criterion.examples_negative
        criterion.examples_borderline = enriched_criterion.examples_borderline

    return output


def enrich_criterion(description: str) -> CriterionEnrichment:
    model = init_chat_model(
        model="gpt-4o-mini",
        model_provider="openai",
        temperature=0,
    )

    prompt = hub.pull("enrich-scorecard-criterion")
    structured_model = model.with_structured_output(CriterionEnrichment)

    chain = prompt | structured_model
    output = chain.invoke(description)

    return output
