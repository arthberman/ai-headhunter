from datetime import datetime
from typing import cast

from langchain_core.runnables import RunnableConfig, RunnableLambda

from analysis.configuration import Configuration
from analysis.models.synthesis import SynthesisOverall
from analysis.state import MainGraphState
from utils import (
    compute_must_score,
    format_data,
    format_scored_criteria,
    get_extended_scored_criterion,
    get_prompt,
    init_model,
)


def get_evaluation_guidelines(must: bool) -> str:
    """Get the evaluation guidelines for the overall analysis."""
    if not must:
        return (
            "3. In this case, the candidate has failed MUST HAVE criteria, "
            "so the final output is FAIL"
        )

    return """
3. Determine the match conclusion (PASS/FAIL/DOUBT) using these guidelines:
   - PASS: 
     * Shows clear motivation to move
     * Career progression makes sense
     * No major blockers in availability
     * Demonstrates alignment with role expectations
     * Satisfactory performance on NICE TO HAVE criteria

   - FAIL: 
     * Only possible for career alignment issues:
       - Major blockers in availability/openness to work
       - Significant misalignment in career hierarchy/progression

   - DOUBT: 
     * Unclear motivation or timing issues
     * Potential concerns about career fit
     * Mixed performance on NICE TO HAVE criteria (some low, some acceptable)
     * Uncertainty about overall skill alignment
     * Minor concerns about availability or progression

   Evaluation Balance:
   - Poor performance on NICE TO HAVE criteria can only lead to DOUBT, not FAIL
   - Career misalignment (hierarchy/openness) are the only FAIL triggers
   - NICE TO HAVE criteria help differentiate between PASS and DOUBT cases
   - Consider overall profile for PASS vs DOUBT decisions

    Note: Since MUST HAVE criteria are satisfied, only major career misalignment 
         (hierarchy or openness to work) can result in FAIL status."""


def node_conclude(state: MainGraphState, config: RunnableConfig) -> MainGraphState:
    """Conclude the overall analysis."""
    # Load configuration from the provided RunnableConfig
    configuration = Configuration.from_runnable_config(config)

    # Initialize the prompt
    prompt = get_prompt("analysis-conclusion")

    # Initialize the model
    raw_model = init_model(configuration.synthesis_model)
    model = raw_model.with_structured_output(SynthesisOverall)

    # Create the chain
    chain = cast(RunnableLambda, prompt | model)

    # Check if the candidate has satisfied the must-have criteria
    must_score = compute_must_score(state.scored_criterion, state.scorecard)

    # Extend the scored criterion with the scorecard
    extended_scored_criterion = get_extended_scored_criterion(
        state.scored_criterion, state.scorecard
    )

    # Invoke the chain
    res = cast(
        SynthesisOverall,
        chain.invoke(
            {
                "extended_scored_criterion": format_data(
                    format_scored_criteria(
                        extended_scored_criterion,
                        state.scored_criterion,
                        state.scorecard,
                    )
                ),
                "evaluation_guidelines": format_data(
                    get_evaluation_guidelines(
                        False if must_score.score.value == "FAIL" else True
                    )
                ),
                "job_synthesis": format_data(state.job_synthesis),
                "synthesis_hierarchy": format_data(state.synthesis_hierarchy),
                "synthesis_open_to_work": format_data(state.synthesis_open_to_work),
                "inferred_role_trajectory": format_data(state.inferred_role_trajectory),
                "output_language": configuration.output_language,
                "system_time": datetime.now().strftime("%d %B %Y (%d-%m-%Y)"),
            }
        ),
    )

    return {"synthesis_overall": res}
