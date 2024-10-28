from typing import cast

from dotenv import load_dotenv
from langchain import hub
from langchain_core.runnables import Runnable
from langsmith.evaluation import evaluate
from langsmith.schemas import Example, Run

from analysis.nodes.enrichment.language import StructuredOutput
from utils import format_data
from utils.init_model import init_model

load_dotenv(dotenv_path=".env.studio")
load_dotenv(dotenv_path=".env")


def test_language_enrichment(example: dict):
    # Initialize the raw model with the provided configuration
    raw_model = init_model("bedrock_converse/anthropic.claude-3-5-sonnet-20241022-v2:0")

    # Initialize the prompt
    prompt = hub.pull("generate-language-enrichment")

    # Bind the model to the structured output
    model = raw_model.with_structured_output(StructuredOutput)

    # Create the chain
    chain = cast(Runnable, prompt | model)

    # Invoke the chain
    res = cast(
        StructuredOutput,
        chain.invoke({"profile": format_data(example), "knowledge_points": ""}),
    )

    return {"language_proficiency": res.language_proficiency}


def correct_label(root_run: Run, example: Example) -> dict:
    """print("Outputs-" * 100)
    print(root_run.outputs)
    print("-" * 100)
    print("Inputs-" * 100)
    print(root_run.inputs["example"])
    print("-" * 100)
    print("Example-" * 100)
    print(example)"""
    return {"score": 1, "key": "correct_label"}


experiment_results = evaluate(
    test_language_enrichment,
    data="ds-language-enrichment",
    evaluators=[correct_label],
    experiment_prefix="test-language-enrichment",
    metadata={
        "variant": "synthethic data with openai/gpt-4o-mini",
    },
)
