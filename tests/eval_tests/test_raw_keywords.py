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

    return {"res": res.keywords}


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
As an expert evaluator, your task is to assess the quality of keywords extracted from job descriptions by an AI recruiter agent. The evaluation should be based on five key dimensions: Relevance (SEO), Accuracy and Specificity. These dimensions ensure the keywords effectively attract qualified candidates, accurately reflect the job, maintain an appropriate level of detail, promote inclusivity, and are presented in a user-friendly manner.

For each job description and its corresponding extracted keywords, evaluate the following dimensions and provide a score from 1 to 10, along with a brief justification for each score. If applicable, suggest improvements or alternative keywords to enhance the quality of the extraction.
1. Relevance (SEO)

    Definition: How well do the keywords align with search terms that qualified candidates would likely use when looking for this position?
    Scoring:
        1: Keywords are irrelevant to the job or industry, unlikely to be searched by qualified candidates.
        5: Some keywords are relevant, but many are too generic or not specific to the role.
        10: Keywords are highly relevant and match terms commonly used by qualified candidates in job searches.
    Example:
        For a "Data Scientist" role: Relevant keywords might include "machine learning," "Python," or "data analysis." Irrelevant keywords might include "sales" or "customer service."
    Guiding Questions:
        Would qualified candidates use these terms when searching for jobs in this field?
        Do the keywords reflect current industry terminology that job seekers would recognize?
        Are the keywords aligned with how candidates describe their own skills and experience on resumes and profiles?
        Do the keywords include important certifications, tools, or methodologies specific to this field?
        Are trending or emerging terms in the field included where appropriate?

2. Accuracy

    Definition: How correctly do the keywords reflect the essential skills, qualifications, and responsibilities explicitly mentioned in the job description?
    Scoring:
        1: Keywords are incorrect, misleading, or unrelated to the job description.
        5: Keywords partially reflect the job description but miss key elements or include inaccuracies.
        10: Keywords perfectly capture the core skills, qualifications, and responsibilities outlined in the job description.
    Example:
        For a "Software Engineer" role requiring "Java" and "cloud computing": Accurate keywords include "Java" and "cloud computing." Inaccurate keywords might include "C++" if not mentioned.
    Guiding Questions:
        Do the keywords directly appear in or closely paraphrase the job description?
        Are all major skills and qualifications from the job description represented in the keywords?
        Are there keywords that suggest skills or requirements not mentioned in the job description?
        Do the keywords accurately represent the level of expertise required (e.g., "advanced Excel" vs. "Excel")?
        Do the keywords accurately reflect the primary vs. secondary skills in the job description?

3. Specificity

    Definition: Assess whether the set of keywords strikes the right balance between being too narrow and too broad.
    Scoring:
        1: Keywords are too narrow, focusing only on highly specific terms that may exclude qualified candidates.
        5: Keywords achieve an ideal balance, capturing the role’s core while remaining accessible to a diverse candidate pool.
        10: Keywords are too broad, including generic terms that attract unqualified candidates or fail to differentiate the role.
    Example:
        For a "Marketing Manager" role: Too narrow might be "SEO for SaaS startups in APAC"; too broad might be "communication" or "leadership." An ideal set could include "digital marketing," "content strategy," and "team management."
    Guiding Questions:
        Are the keywords specific enough to target the right caliber of candidates?
        Are any keywords so specialized that they might exclude qualified candidates?
        Are any keywords so general that they would attract unqualified candidates?
        Do the keywords appropriately reflect the seniority level of the position?
        Is there a good mix of general field terms and specific skill terms?



Job Description: {inputs}

Extracted Keywords: {outputs}

Reference Keywords: {reference_outputs}
""",
            ),
        ]
    )

    chain = prompt | model

    res = cast(
        EvaluateRawQuery,
        chain.invoke(
            {
                "inputs": inputs,
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
    data="ds-raw-keywords",
    evaluators=[evaluate_raw_keywords],  # type: ignore
    experiment_prefix="raw_keywords",
)
