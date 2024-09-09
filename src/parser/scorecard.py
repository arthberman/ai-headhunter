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


def parse_scorecard(raw_job_posting: str) -> Scorecard:
    model = init_chat_model(
        model="gpt-4o-2024-08-06",
        model_provider="openai",
        temperature=0,
    )
    structured_model = model.with_structured_output(Scorecard)
    prompt = hub.pull("parser-scorecard")

    chain = prompt | structured_model
    output: Scorecard = chain.invoke(raw_job_posting)

    for criterion in output.mustHaveCriteria.criteria:
        enriched_criterion = enrich_criterion(raw_job_posting, criterion.description)
        criterion.guidelines = enriched_criterion.guidelines
        criterion.examples_positive = enriched_criterion.examples_positive
        criterion.examples_negative = enriched_criterion.examples_negative

    return output


def enrich_criterion(
    raw_job_posting: str, criterion_description: str
) -> CriterionEnrichment:
    model = init_chat_model(
        model="claude-3-5-sonnet-20240620",
        model_provider="anthropic",
        temperature=0,
    )

    prompt = hub.pull("enrich-scorecard-criterion")
    structured_model = model.with_structured_output(CriterionEnrichment)

    chain = prompt | structured_model
    output = chain.invoke(
        {
            "criterion_description": criterion_description,
            "job_posting": raw_job_posting,
        }
    )

    return output
