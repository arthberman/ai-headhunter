from typing import List, cast

from dotenv import load_dotenv
from utils import get_hub_prompt
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable
from langsmith.evaluation import evaluate
from langsmith.schemas import Example, Run
from pydantic import BaseModel, Field
from trustcall import create_extractor

from scorecard.models.question import ListQuestions
from utils.init_model import init_model

load_dotenv(dotenv_path=".env.studio")
load_dotenv(dotenv_path=".env")


def predict_questions(example: dict):
    prompt = get_hub_prompt("generate-scorecard-questions")
    chat_prompt = ChatPromptTemplate.from_messages(prompt.messages)

    formatted_messages = chat_prompt.format_messages(
        raw_job_posting=example["raw_job_posting"], web_context=example["web_context"]
    )

    raw_model = init_model("openai/gpt-4o")

    extractor = create_extractor(
        raw_model, tools=[ListQuestions], tool_choice="ListQuestions"
    )

    res = cast(
        ListQuestions,
        extractor.invoke(
            {
                "messages": formatted_messages,
            }
        )["responses"][0],
    )

    return res


def judge_evaluator_criteria(root_run: Run, example: Example) -> dict:
    class GradeCriterion(BaseModel):
        """A numerical score for criterion relevancy."""

        score: int = Field(description="Criterion score from 1 to 10")
        explanation: str = Field(
            description="Explanation for the score, max 100 characters"
        )

    class GradeQuestions(BaseModel):
        """A numerical score for question relevancy."""

        questions: List[GradeCriterion] = Field(
            description="List of criterion scores and explanations"
        )

    prompt = get_hub_prompt("eval-judge-scorecard-questions-criteria")
    raw_model = init_model(
        "bedrock_converse/us.anthropic.claude-3-5-sonnet-20241022-v2:0"
    )
    model = raw_model.with_structured_output(GradeQuestions)

    chain = cast(Runnable, prompt | model)
    res = cast(
        GradeQuestions,
        chain.invoke({"input": example.inputs, "output": root_run.outputs}),
    )

    scores = [q.score for q in res.questions]

    metrics = [
        {
            "key": "mean_score",
            "score": sum(scores) / len(scores),  # Overall performance
        },
        {
            "key": "min_score",
            "score": min(scores),  # Worst-case detection
        },
        {
            "key": "critical_issues",
            "score": sum(1 for s in scores if s < 5)
            / len(scores),  # Proportion of low scores
        },
    ]

    return {"results": metrics}


def judge_evaluator_reference(root_run: Run, example: Example) -> dict:
    class GradeScore(BaseModel):
        """A numerical score for question relevancy."""

        score: int = Field(description="Score from 1 to 10")
        explanation: str = Field(description="Explanation for the score")

    prompt = get_hub_prompt("eval-judge-scorecard-questions")
    raw_model = init_model(
        "bedrock_converse/us.anthropic.claude-3-5-sonnet-20241022-v2:0"
    )
    model = raw_model.with_structured_output(GradeScore)

    chain = cast(Runnable, prompt | model)
    res = cast(
        GradeScore,
        chain.invoke({"prediction": root_run.outputs, "reference": example.outputs}),
    )

    return {"results": [{"key": "reference_score", "score": res.score}]}


experiment_results = evaluate(
    predict_questions,
    data="ds-scorecard-questions",
    evaluators=[judge_evaluator_criteria, judge_evaluator_reference],
    experiment_prefix="test-scorecard-questions",
    metadata={
        "variant": "synthethic data",
    },
)
