from typing import cast

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable
from langsmith.evaluation import evaluate
from openevals.llm import create_llm_as_judge
from openevals.prompts import CORRECTNESS_PROMPT
from pydantic import BaseModel, Field

from feeder.models.raw_query import RawQuery
from utils.get_prompt import get_prompt
from utils.init_model import init_model

instructions = """
Evaluate the raw query generated for the job description against the given reference ourputs and rate them in the following format.

Relevance: 1-5
Accuracy: 1-5
Specificity: 1-5

Evaluation Criteria:
- Relevance: How SEO friendly the keywords are
- Accuracy: How factually correct the keywords are
- Specificity: How broad or narrow the keywords are
"""


class RawQueryEvaluationResponse(BaseModel):
    """Response model for evaluation of raw query"""

    relevancy: int = Field(
        ...,
        gt=0,
        lt=6,
        description="Rating for how SEO friendly the keywords are",
    )
    accuracty: int = Field(
        ...,
        gt=0,
        lt=6,
        description="Rating for how factually correct the keywords are",
    )
    specificity: int = Field(
        ..., gt=0, lt=6, description="Rating for how broad or narrow the keywords are"
    )


def target(job_description: dict):
    """Generate a raw query from given job description"""
    raw_model = init_model(
        "bedrock_converse/us.anthropic.claude-3-5-sonnet-20241022-v2:0"
    )

    prompt = get_prompt("first_gen_json_object_prompt")

    model = raw_model.with_structured_output(RawQuery)

    chain = cast(Runnable, prompt | model)

    res = cast(RawQuery, chain.invoke({"job_offer_description": job_description}))

    return {"res": res}


def accuracy(outputs: dict, reference_outputs: dict):
    """Evaluate the accuracy of the generated raw query"""
    raw_model = init_model(
        "bedrock_converse/us.anthropic.claude-3-5-sonnet-20241022-v2:0"
    )
    model = raw_model.with_structured_output(RawQueryEvaluationResponse)

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", instructions),
            (
                "user",
                f"""Reference Outputs: {reference_outputs};
            Generated Outputs: {outputs}""",
            ),
        ]
    )

    chain = prompt | model

    res = cast(RawQueryEvaluationResponse, chain.invoke({}))

    return res


experiment_results = evaluate(
    target,
    data="ds-raw-query",
    evaluators=[accuracy],
    experiment_prefix="test-raw-query",
)
