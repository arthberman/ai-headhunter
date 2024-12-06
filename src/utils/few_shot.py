from dataclasses import dataclass
from typing import List

from langchain_core.messages import BaseMessage
from langchain_core.prompts import ChatPromptTemplate, FewShotChatMessagePromptTemplate

from utils.get_dataset import get_dataset


@dataclass
class FewShotConfig:
    """Few shot configuration."""

    dataset_name: str
    input_keys: List[str]
    output_keys: List[str]
    input_template: str
    output_template: str


async def get_few_shot_messages(config: FewShotConfig) -> List[BaseMessage]:
    """Generate few-shot example messages based on configuration."""
    # Load dataset
    fs_dataset = get_dataset(config.dataset_name)

    # Build examples dictionary
    examples = []
    for example in fs_dataset:
        example_dict = {}
        # Add inputs
        for key in config.input_keys:
            example_dict[key] = example.inputs[key]
        # Add outputs
        for key in config.output_keys:
            example_dict[key] = example.outputs[key]
        examples.append(example_dict)

    # Create prompt template
    example_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "human",
                f"Few shot example\n\nInput:\n{config.input_template}\n\nOutput:\n{config.output_template}",
            ),
        ]
    )

    # Create few-shot prompt
    few_shot_prompt = FewShotChatMessagePromptTemplate(
        example_prompt=example_prompt,
        examples=examples,
    )

    return (await few_shot_prompt.ainvoke({})).to_messages()
