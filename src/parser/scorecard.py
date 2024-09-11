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


class CriterionWithContext(BaseModel):
    criterion_description: str = Field(
        description="Description of the criterion.",
    )
    criterion_context: str = Field(
        description="Context of the criterion. This is the context related to the criterion.",
    )


class ListCriterionWithContext(BaseModel):
    criteria: List[CriterionWithContext] = Field(
        description="List of criteria with context.",
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

    criteria_with_context = enrich_criterion_with_context(output, raw_job_posting)

    # Create a dictionary for easier lookup
    context_dict = {
        c.criterion_description: c.criterion_context
        for c in criteria_with_context.criteria
    }

    # Update output with context for each criterion
    for criterion in (
        output.mustHaveCriteria.criteria
        + output.importantCriteria.criteria
        + output.niceToHaveCriteria.criteria
    ):
        if criterion.description is not None and criterion.description in context_dict:
            criterion.context = context_dict[criterion.description]
        else:
            print(
                f"Warning: No context found for criterion with description: {criterion.description}"
            )
            criterion.context = ""  # Set a default empty context

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


def enrich_criterion_with_context(
    scorecard: Scorecard, raw_job_posting: str
) -> ListCriterionWithContext:
    model = init_chat_model(
        model="gpt-4o-2024-08-06",
        model_provider="openai",
        temperature=0,
    )

    prompt = hub.pull("parser-scorecard-context")
    structured_model = model.with_structured_output(ListCriterionWithContext)

    # List of all criteria (mustHaveCriteria and importantCriteria and niceToHaveCriteria) with id and description
    scorecard_criteria = [
        {"description": criterion.description}
        for criterion in scorecard.mustHaveCriteria.criteria
        + scorecard.importantCriteria.criteria
        + scorecard.niceToHaveCriteria.criteria
    ]

    chain = prompt | structured_model
    output = chain.invoke(
        {
            "scorecard_criteria": scorecard_criteria,
            "raw_job_posting": raw_job_posting,
        }
    )

    return output
