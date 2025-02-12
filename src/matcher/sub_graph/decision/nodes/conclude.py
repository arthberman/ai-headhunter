from datetime import datetime
from typing import cast

from langchain_core.runnables import RunnableConfig, RunnableLambda

from matcher.configuration import Configuration
from matcher.state import MainGraphState
from matcher.sub_graph.decision.models import Conclusion, DecisionType
from matcher.sub_graph.infer_enrichment.models import InferredAttributeType
from utils import (
    compute_required_score,
    format_scored_criteria,
    get_extended_scored_criterion,
    get_prompt,
    init_model,
)


def get_evaluation_guidelines(must: bool) -> str:
    """Get the evaluation guidelines for the overall matcher."""
    if not must:
        return (
            "3. In this case, the candidate has failed required criteria, "
            "so the final output is REJECTED"
        )

    return """
3. Determine the match conclusion (ACCEPTED/REJECTED/REVIEW) using these guidelines:
   - ACCEPTED: 
     * Shows clear motivation to move
     * Career progression makes sense
     * No major blockers in availability
     * Demonstrates alignment with role expectations
     * Satisfactory performance on preferred criteria

   - REJECTED: 
     * Only possible for career alignment issues:
       - Major blockers in availability/openness to work
       - Significant misalignment in career hierarchy/progression

   - REVIEW: 
     * Unclear motivation or timing issues
     * Potential concerns about career fit
     * Mixed performance on preferred criteria (some low, some acceptable)
     * Uncertainty about overall skill alignment
     * Minor concerns about availability or progression

   Evaluation Balance:
   - Poor performance on preferred criteria can only lead to REVIEW, not REJECTED
   - Career misalignment (hierarchy/openness) are the only REJECTED triggers
   - Preferred criteria help differentiate between ACCEPTED and REVIEW cases
   - Consider overall profile for ACCEPTED vs REVIEW decisions

    Note: Since required criteria are satisfied, only major career misalignment 
         (hierarchy or openness to work) can result in REJECTED status."""


async def node_conclude(
    state: MainGraphState, config: RunnableConfig
) -> MainGraphState:
    """Conclude the overall matcher."""
    # Load configuration from the provided RunnableConfig
    configuration = Configuration.from_runnable_config(config)

    # Initialize the prompt
    prompt = get_prompt("analysis-conclusion")

    # Initialize the model
    raw_model = init_model(configuration.synthesis_model)
    model = raw_model.with_structured_output(Conclusion)

    # Create the chain
    chain = cast(RunnableLambda, prompt | model)

    # Check if the candidate has satisfied the must-have criteria
    required_score = compute_required_score(state.scored_criterion, state.scorecard)

    # Extend the scored criterion with the scorecard
    extended_scored_criterion = get_extended_scored_criterion(
        state.scored_criterion, state.scorecard
    )

    # Invoke the chain
    res = cast(
        Conclusion,
        await chain.ainvoke(
            {
                "extended_scored_criterion": format_scored_criteria(
                    extended_scored_criterion,
                    state.scored_criterion,
                    state.scorecard,
                ).model_dump(mode="json"),
                "evaluation_guidelines": get_evaluation_guidelines(
                    False if required_score.outcome.value == "rejected" else True
                ),
                "job_synthesis": state.job_synthesis,
                "synthesis_hierarchy": state.get_decision(
                    DecisionType.HIERARCHY_MOVE
                ).explanation,
                "decision_openess_to_work": state.get_decision(
                    DecisionType.OPENESS_TO_WORK
                ).explanation,
                "inferred_role_trajectory": state.get_inferred_attribute(
                    InferredAttributeType.ROLE_TRAJECTORY
                ).description,
                "output_language": configuration.output_language,
                "system_time": datetime.now().strftime("%B %d, %Y (%Y-%m-%-d)"),
            }
        ),
    )

    return {"conclusion": res}
