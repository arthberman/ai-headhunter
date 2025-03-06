from typing import cast

from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable
from langsmith.evaluation import evaluate
from pydantic import BaseModel, Field

from src.feeder.models.raw_query import RawQuery
from utils.get_prompt import get_prompt
from utils.init_model import init_model

load_dotenv(dotenv_path=".env.studio")


class EvaluateRawQuery(BaseModel):
    relevancy: int = Field(
        ...,
        description="How SEO friendly are the keywords for the given job description",
    )
    accuracy: int = Field(..., description="How accurate are the keywords for the job")
    specificity: int = Field(..., description="Rates the specificity of the keywords")


def target(job_description: dict):
    """Generate a raw query from given job description"""
    raw_model = init_model("openai/gpt-4o")

    prompt = get_prompt("first_gen_json_object_prompt")

    model = raw_model.with_structured_output(RawQuery)

    chain = cast(Runnable, prompt | model)

    res = cast(
        RawQuery,
        chain.invoke({"job_offer_description": job_description, "query_memory": None}),
    )

    return {"res": res.not_in_job_titles}


def evaluate_raw_not_in_job_titles(
    inputs: dict, outputs: dict, reference_outputs: dict
) -> list[dict]:
    raw_model = init_model("openai/gpt-4o")
    model = raw_model.with_structured_output(EvaluateRawQuery)

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """
    As an expert evaluator, your task is to assess the quality of "not_in_job_titles" extracted from job descriptions by an AI recruiter agent. These titles represent positions that should be excluded from the recruitment targeting as they would not match the qualifications or responsibilities of the role. Your evaluation will focus on three key dimensions: Exclusion Relevance, Accuracy of Mismatch, and Exclusion Scope.

    Evaluation Dimensions
    Your evaluation will focus on three key dimensions, using a 1-10 scale:

    1. Exclusion Relevance (1-10)

        Definition: How appropriate is it to exclude these job titles from search targeting? This measures whether the excluded titles represent roles that would genuinely be inappropriate for the position or would lead to unqualified applicants.
        Guiding Questions:

        Would including these titles in recruitment targeting likely attract candidates who lack the necessary qualifications?
        Are these titles different enough from the target role to warrant exclusion?
        Would candidates with these job titles typically lack the core skills required for the position?
        Do these excluded titles represent fundamentally different career paths or specializations?
        Are there legitimate reasons why these titles should be excluded rather than included?

        Scoring Guide:

        1-2: The excluded titles should actually be included; they represent highly relevant roles
        3-4: Many excluded titles are borderline relevant and could potentially be included
        5-6: Most excluded titles are appropriate, though some borderline cases exist
        7-8: The excluded titles are appropriate and would generally attract unqualified candidates
        9-10: The excluded titles perfectly represent roles that would be entirely inappropriate for the position

    2. Accuracy of Mismatch (1-10)
        Definition: How correctly do these excluded job titles reflect positions that would truly be misaligned with the actual role? This measures whether the exclusions accurately identify titles that represent skills, experience, or qualifications that don't match the job requirements.
        Guiding Questions:

        Do these titles represent skill sets that genuinely don't overlap with the requirements?
        Would the day-to-day responsibilities of these excluded roles be fundamentally different?
        Are the excluded titles from entirely different departments or functions?
        Is there a clear mismatch between the level of responsibility in the excluded titles and the role?
        Do the excluded titles accurately represent positions that would lack the technical or specialized knowledge required?

        Scoring Guide:

        1-2: Excluded titles have substantial skill and responsibility overlap with the actual role
        3-4: Excluded titles have moderate overlap and could potentially be qualified
        5-6: Most excluded titles have limited overlap, with some exceptions
        7-8: Excluded titles generally have very little skill or responsibility overlap
        9-10: Excluded titles have no relevant skill or responsibility overlap whatsoever

    3. Exclusion Scope (1-10)
        Definition: Assess whether the set of excluded job titles is appropriately scoped—neither too narrow (excluding too few unqualified positions) nor too broad (excluding potentially qualified candidates). For this dimension, a score of 5 is ideal.
        Guiding Questions:

        Does the exclusion list omit any obvious unrelated roles that should be excluded?
        Does the exclusion list mistakenly include titles that might be qualified for the role?
        Is the scope of exclusions appropriate for the specificity of the role itself?
        Are the exclusions at an appropriate level of granularity (not too general or too specific)?
        Do the exclusions account for cross-functional roles that might have relevant skills?

        Scoring Guide:

        1: Far too few exclusions, missing many obvious unrelated roles
        2-3: Insufficient exclusions, allowing many unqualified candidates
        4: Slightly too few exclusions
        5: Ideal scope of exclusions, balanced and appropriate
        6: Slightly too many exclusions
        7-8: Overly broad exclusions, potentially eliminating qualified candidates
        9-10: Excessively broad exclusions, eliminating many qualified candidates


    Job description: {inputs}

    Extracted not_in_job_titles: {outputs}

    Reference not_in_job_titles: {reference_outputs}
    """,
            )
        ]
    )

    chain = prompt | model

    res = cast(
        EvaluateRawQuery,
        chain.invoke(
            {
                "inputs": inputs["input"]["job_description"],
                "reference_outputs": reference_outputs,
                "outputs": outputs["res"],
            }
        ),
    )

    return [
        {
            "key": "relevancy",
            "score": res.relevancy,
        },
        {
            "key": "accuracy",
            "score": res.accuracy,
        },
        {
            "key": "specificity",
            "score": res.specificity,
        },
    ]


experiment_results = evaluate(
    target,
    data="ds-raw-not-in-job-titles",
    evaluators=[evaluate_raw_not_in_job_titles],  # type: ignore
    experiment_prefix="raw_not_in_job_titles",
)
