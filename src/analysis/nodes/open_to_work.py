from datetime import datetime
from typing import Optional, cast

from langchain_core.prompts import ChatPromptTemplate, FewShotChatMessagePromptTemplate
from langchain_core.runnables import Runnable, RunnableConfig

from analysis.full.configuration import Configuration
from analysis.full.state import MainGraphState
from analysis.models.synthesis import OpenToWorkSynthesis, SynthesisScore
from utils import get_candidate_timeline, get_dataset, get_prompt, init_model


def node_open_to_work(state: MainGraphState, config: Optional[RunnableConfig] = None):
    """Analyze the candidate's openess to work, awareness of new opportunities."""
    # Load configuration from the provided RunnableConfig
    configuration = Configuration.from_runnable_config(config)

    # Already open to work on his profile
    if state.profile.is_open_to_work:
        return {
            "synthesis_open_to_work": OpenToWorkSynthesis(
                score=SynthesisScore.PASS,
                explanation="This candidate is declared as Open To Work on his profile.",
            )
        }

    # Initialize the raw model with the provided configuration
    raw_model = init_model(configuration.analysis_model)

    # Initialize the prompt
    prompt = get_prompt("candidate-analysis-open-to-work")

    # Few shot
    fs_dataset = get_dataset("fs-candidate-analysis-open-to-work")
    examples = [
        {
            "profile_details": example.inputs["profile_details"],
            "score": example.outputs["score"],
            "explanation": example.outputs["explanation"],
        }
        for example in fs_dataset
    ]

    example_prompt = ChatPromptTemplate.from_messages(
        [
            ("human", "Profile details: {profile_details}"),
            (
                "ai",
                """
                Score: {score}
                Explanation: {explanation}
                """,
            ),
        ]
    )

    few_shot_prompt = FewShotChatMessagePromptTemplate(
        example_prompt=example_prompt,
        examples=examples,
    )

    # Bind the model to the structured output
    model = raw_model.with_structured_output(OpenToWorkSynthesis)

    # Create the chain
    chain = cast(Runnable, prompt | model)

    # Invoke the chain
    res = cast(
        OpenToWorkSynthesis,
        chain.invoke(
            {
                "candidate_timeline": get_candidate_timeline(
                    state.profile, with_detail=True
                ),
                "examples": few_shot_prompt.invoke({}).to_messages(),
                "target_role": state.job_synthesis,
                "output_language": configuration.output_language,
                "system_time": datetime.now().isoformat(),
            }
        ),
    )

    return {"synthesis_open_to_work": res}
