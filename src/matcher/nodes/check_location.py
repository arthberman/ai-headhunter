from datetime import datetime
from typing import cast

from langchain_core.runnables import RunnableConfig, RunnableLambda

from matcher.configuration import Configuration
from matcher.models.synthesis import (
    LocationSynthesis,
    SynthesisScore,
)
from matcher.state import MainGraphState
from matcher.sub_graph.criterion_matcher.models import ScoredCriterion
from matcher.sub_graph.decision.models import ConclusionOverall
from setup.models.scorecard import Category, Priority
from utils import get_prompt, init_model
from utils.candidate_timeline import get_candidate_timeline
from utils.few_shot import FewShotConfig, get_few_shot_messages


async def node_check_location(
    state: MainGraphState, config: RunnableConfig
) -> MainGraphState:
    """Analyze the candidate's location."""
    # Load configuration from the provided RunnableConfig
    configuration = Configuration.from_runnable_config(config)

    # Initialize the prompt
    prompt = get_prompt("candidate-analysis-location")

    # Few shot
    few_shot_config = FewShotConfig(
        dataset_name="fs-candidate-analysis-location",
        input_keys=["profile_details", "job_criteria"],
        output_keys=["score", "explanation"],
        input_template="Profile details: {profile_details}\nJob criteria: {job_criteria}",
        output_template="Score: {score}\nExplanation: {explanation}",
    )

    few_shot_messages = await get_few_shot_messages(few_shot_config)

    # Initialize the model
    raw_model = init_model(configuration.matcher_model)
    model = raw_model.with_structured_output(LocationSynthesis)

    # Create the chain
    chain = cast(RunnableLambda, prompt | model)

    # Get the first scorecard criteria of type location
    criterion = next(
        criterion
        for criterion in state.scorecard.criteria
        if criterion.category == Category.LOCATION
        and criterion.priority == Priority.REQUIRED
    )

    res = cast(
        LocationSynthesis,
        await chain.ainvoke(
            {
                "job_location_criteria": criterion.model_dump(mode="json"),
                "candidate_timeline": get_candidate_timeline(state.profile).model_dump(
                    mode="json"
                ),
                "candidate_headline_location": state.profile.location,
                "examples": few_shot_messages,
                "output_language": configuration.output_language,
                "system_time": datetime.now().strftime("%B %d, %Y (%Y-%m-%-d)"),
            }
        ),
    )

    # confidence is 1 if the score is PASS, 0.5 if DOUBT, 0 otherwise
    scored_criterion = ScoredCriterion(
        id=criterion.id,
        score=1
        if res.score == SynthesisScore.PASS
        else 0.5
        if res.score == SynthesisScore.DOUBT
        else 0,
        explanation=res.explanation,
        confidence=1
        if res.score == SynthesisScore.PASS
        else 0.5
        if res.score == SynthesisScore.DOUBT
        else 0,
    )

    # Create a state update dictionary
    state_update = {
        "synthesis_location": res,
        "scored_criterion": [scored_criterion],
    }

    # Only update synthesis_overall if location check fails
    if res.score == SynthesisScore.FAIL:
        state_update["conclusion_overall"] = ConclusionOverall(
            score=SynthesisScore.FAIL,
            explanation=f"Required location criteria not met: {res.explanation}",
            summary=[
                "🚫 Location requirements not satisfied",
                "📍 Candidate location incompatible with job requirements",
            ],
        )

    return state_update
