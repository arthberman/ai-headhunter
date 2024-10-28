from typing import List, cast

from dotenv import load_dotenv
from langchain import hub
from langchain_core.runnables import Runnable
from langsmith.evaluation import evaluate
from langsmith.schemas import Example, Run

from analysis.models.language import LanguageProficiency
from analysis.nodes.enrichment.language import StructuredOutput
from utils import format_data
from utils.init_model import init_model

load_dotenv(dotenv_path=".env.studio")
load_dotenv(dotenv_path=".env")


def predict_language_enrichment(example: dict):
    # Initialize the raw model with the provided configuration
    raw_model = init_model(
        "bedrock_converse/us.us.anthropic.claude-3-5-sonnet-20241022-v2:0"
    )

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


def convert_to_language_proficiency(reference: list[dict]) -> list[LanguageProficiency]:
    """
    Convert a list of language proficiency dictionaries to LanguageProficiency objects.

    Args:
        reference (list[dict]): List of dictionaries containing language proficiency data

    Returns:
        list[LanguageProficiency]: List of LanguageProficiency objects
    """
    return [
        LanguageProficiency(
            language=item["language"],
            proficiency=item["proficiency"],
            explanation=item["explanation"],
        )
        for item in reference
    ]


def correct_label(root_run: Run, example: Example) -> dict:
    # input_profile = cast(Profile, example.inputs["profile"])
    reference = convert_to_language_proficiency(example.outputs["language_proficiency"])
    prediction = cast(
        List[LanguageProficiency], root_run.outputs["language_proficiency"]
    )

    # Convert prediction and reference to sets of (language, proficiency) tuples
    reference_set = {(lang.language, lang.proficiency) for lang in reference}
    prediction_set = {(lang.language, lang.proficiency) for lang in prediction}

    # Calculate true positives, false positives, and false negatives
    true_positives = len(reference_set.intersection(prediction_set))
    false_positives = len(prediction_set - reference_set)
    false_negatives = len(reference_set - prediction_set)

    # Handle edge case where there are no true positives
    if true_positives == 0:
        return {
            "results": [
                {"key": "f1_score", "score": 0.0},
                {"key": "precision", "score": 0.0},
                {"key": "recall", "score": 0.0},
            ]
        }

    # Compute precision and recall
    precision = true_positives / (true_positives + false_positives)
    recall = true_positives / (true_positives + false_negatives)

    # Calculate F1 score
    f1_score = 2 * (precision * recall) / (precision + recall)

    return {
        "results": [
            {"key": "f1_score", "score": f1_score},
            {"key": "precision", "score": precision},
            {"key": "recall", "score": recall},
        ]
    }


experiment_results = evaluate(
    predict_language_enrichment,
    data="ds-language",
    evaluators=[correct_label],
    experiment_prefix="test-language-enrichment",
    metadata={
        "variant": "synthethic data",
    },
)
