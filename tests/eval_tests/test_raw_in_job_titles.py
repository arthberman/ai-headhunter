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
    specificity: int = Field(
        ...,
        description="Rates the specificity of the keywords if its too broad or narror or ideal",
    )


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

    return {"res": res.in_job_titles}


def evaluate_raw_keywords(
    inputs: dict, outputs: dict, reference_outputs: dict
) -> list[dict]:
    raw_model = init_model("openai/gpt-4o")
    model = raw_model.with_structured_output(EvaluateRawQuery)

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """
As an expert evaluator, your task is to assess the quality of "in_job_titles" extracted from job descriptions by an AI recruiter agent. These titles represent the core roles typically responsible for the tasks and responsibilities described, and they should reflect the most common job titles associated with those duties in the relevant industry. Your evaluation will focus on three key dimensions: Relevance to Core Responsibilities, Accuracy to Common Titles, and Appropriateness of Scope. For each job description and its corresponding "in_job_titles," provide a score from 1 to 5 for each dimension, along with a brief justification. Additionally, if applicable, suggest improvements or alternative titles that better align with industry norms and common usage.

1. Relevance to Core Responsibilities

    Definition: Measures how well the extracted "in_job_titles" align with the primary tasks and responsibilities outlined in the job description.
    Scoring:
        1: Titles have little to no connection to the responsibilities described.
        5: Titles relate to some responsibilities but miss critical aspects of the role.
        10: Titles fully reflect the core responsibilities and tasks of the role.
    Example:
        For a job description centered on developing software applications:
            Score 1: "Customer Support Specialist" or "Marketing Coordinator" are unrelated to software development.
            Score 5: "IT Support Engineer" relates to tech but not directly to development tasks.
            Score 10: "Software Developer" or "Application Engineer" directly match the core duties.
    Guiding Questions:
        Do the titles reflect the primary functions described in the job posting?
        Would a person with this job title typically perform the listed responsibilities?
        Are the most critical aspects of the role represented in the titles?

2. Accuracy to Common Titles

    Definition: Evaluates how well the extracted "in_job_titles" match the most common and widely recognized job titles for the role, considering industry standards and typical terminology.
    Scoring:
        1: Titles are uncommon, incorrect, or misleading for the role described.
        5: Titles are somewhat aligned with common usage but may not be the most typical or precise options.
        10: Titles are the most commonly accepted and accurate for the role in the industry.
    Example:
        For a job description requiring data analysis with SQL expertise:
            Score 1: "Data Engineer" or "Statistician" may be related but aren’t the most common titles for this role.
            Score 5: "Business Intelligence Analyst" is close but less common than the standard title.
            Score 10: "Data Analyst" is the most widely recognized title for this responsibility.
    Guiding Questions:
        Are these the titles most commonly used in job postings for this type of role?
        Would professionals in this field recognize and identify with these titles?
        Do the titles reflect current industry terminology rather than outdated or uncommon terms?
        Are the titles aligned with how the industry typically categorizes this type of work?

3. Appropriateness of Scope

    Definition: Assesses whether the "in_job_titles" are appropriately scoped—not too broad to lose meaning, nor too narrow to exclude common variations of the role.
    Scoring:
        1: Titles are either overly narrow (e.g., focusing on a tiny subset of duties) or excessively broad (e.g., applicable to unrelated roles).
        5: Titles strike a reasonable balance, capturing the role’s core while allowing for typical variations.
        10: Titles are ideally scoped, perfectly matching the role’s responsibilities without being too restrictive or vague.
    Example:
        For a job description for a marketing leadership role:
            Score 1 (Too Narrow): "Social Media Marketing Specialist" focuses on one aspect, missing the broader leadership scope.
            Score 10 (Too Broad): "Director" could apply to any field, not just marketing.
            Score 5: "Marketing Manager" is ideal, encompassing the role without over- or under-specifying.
    Guiding Questions:
        Is the title specific enough to differentiate this role from others in the organization?
        Is the title broad enough to capture the full range of responsibilities?
        Would the title exclude qualified candidates due to overly specific terminology?
        Would the title attract too many unqualified candidates due to being too general?
        Does the title reflect the appropriate seniority level indicated in the job description?


Job Description: {inputs}

Extracted in_job_titles: {outputs}

Reference in_job_titles: {reference_outputs}
""",
            ),
        ]
    )

    chain = prompt | model

    res = cast(
        EvaluateRawQuery,
        chain.invoke(
            {
                "inputs": inputs["input"]["job_offer_description"],
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
    data="ds-raw-in-job-titles",
    evaluators=[evaluate_raw_keywords],  # type: ignore
    experiment_prefix="raw_in_job_titles",
)
