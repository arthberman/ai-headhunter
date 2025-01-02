from typing import List, cast

from dotenv import load_dotenv
from langchain_core.runnables import Runnable
from langsmith.evaluation import evaluate
from langsmith.schemas import Example, Run
from pydantic import BaseModel, Field

from setup.nodes.scorecard_structure import node_scorecard_structure
from setup.state import ScorecardGraphState
from utils import get_prompt
from utils.init_model import init_model

load_dotenv(dotenv_path=".env.studio")
load_dotenv(dotenv_path=".env")


def predict_structure(example: dict):
    state = ScorecardGraphState(**example)
    res = node_scorecard_structure(state)
    return {"scorecard": res["scorecard"]}


def judge_evaluator_criteria(root_run: Run, example: Example) -> dict:
    class GradeCriterion(BaseModel):
        """A numerical score for criterion relevancy."""

        score: int = Field(description="Criterion score from 1 to 10")
        explanation: str = Field(
            description="Explanation for the score, max 100 characters"
        )

    class GradeCriteria(BaseModel):
        """A numerical score for criterion relevancy."""

        criteria: List[GradeCriterion] = Field(
            description="List of criterion scores and explanations"
        )

    prompt = get_prompt("eval-judge-scorecard-structure-criteria")
    raw_model = init_model(
        "bedrock_converse/us.anthropic.claude-3-5-sonnet-20241022-v2:0"
    )
    model = raw_model.with_structured_output(GradeCriteria)

    chain = cast(Runnable, prompt | model)

    res = cast(
        GradeCriteria,
        chain.invoke({"scorecard": root_run.outputs["scorecard"]}),
    )

    scores = [q.score for q in res.criteria]

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


experiment_results = evaluate(
    predict_structure,
    data="ds-scorecard-structure",
    evaluators=[judge_evaluator_criteria],
    experiment_prefix="test-scorecard-structure",
    metadata={},
)
