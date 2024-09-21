from typing import List

from langchain import hub
from langchain.chat_models import init_chat_model
from pydantic import BaseModel, Field

from scorecard_generator.state import ScorecardGraphState


class CriterionWithContext(BaseModel):
    criterion_description: str = Field(
        description="Description of the criterion.",
    )
    criterion_context: str = Field(
        description="Context of the criterion. This is the context related to the criterion.",
    )


class ListCriterionWithContext(BaseModel):
    criteria: List[CriterionWithContext] = Field(
        description="List of criteria with context.",
    )


def node_generate_context(state: ScorecardGraphState) -> ScorecardGraphState:
    prompt = hub.pull("parser-scorecard-context")

    model = init_chat_model(
        model="gpt-4o-2024-08-06",
        model_provider="openai",
        temperature=0,
    )

    prompt = hub.pull("parser-scorecard-context")
    structured_model = model.with_structured_output(ListCriterionWithContext)

    scorecard_criteria = [
        {"description": criterion.description}
        for criterion in state.scorecard.mustHaveCriteria
        + state.scorecard.importantCriteria
        + state.scorecard.niceToHaveCriteria
    ]

    chain = prompt | structured_model
    output: ListCriterionWithContext = chain.invoke(
        {
            "raw_job_posting": state.raw_job_posting,
            "web_context": state.web_context,
            "human_context": state.human_context,
            "scorecard_criteria": scorecard_criteria,
        }
    )

    # Create a dictionary for easier lookup
    context_dict = {
        c.criterion_description: c.criterion_context for c in output.criteria
    }

    new_scorecard = state.scorecard
    # Update output with context for each criterion
    for criterion in (
        new_scorecard.mustHaveCriteria
        + new_scorecard.importantCriteria
        + new_scorecard.niceToHaveCriteria
    ):
        if criterion.description is not None and criterion.description in context_dict:
            criterion.context = context_dict[criterion.description]
        else:
            print(
                f"Warning: No context found for criterion with description: {criterion.description}"
            )
            criterion.context = ""  # Set a default empty context

    return {"scorecard": new_scorecard}
