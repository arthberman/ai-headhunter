from typing import List

from langchain import hub
from langchain.chat_models import init_chat_model
from scorecard.state import ScorecardGraphState


from scorecard.models.question import ListQuestions


def node_generate_questions(state: ScorecardGraphState) -> ScorecardGraphState:
    prompt = hub.pull("scorecard-enrichment-questions")

    model = init_chat_model(
        model="gpt-4o-2024-08-06", model_provider="openai", temperature=0
    ).with_structured_output(ListQuestions)

    chain = prompt | model

    res = chain.invoke(
        {
            "raw_job_posting": state.raw_job_posting,
            "global_context": state.global_context,
        }
    )

    return {"questions": res}
