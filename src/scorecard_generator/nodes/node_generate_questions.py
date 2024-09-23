from langchain import hub
from langchain.chat_models import init_chat_model

from scorecard_generator.models.question import ListQuestions
from scorecard_generator.state import ScorecardGraphState


def node_generate_questions(state: ScorecardGraphState) -> ScorecardGraphState:
    """Generate questions for the scorecard criteria."""
    prompt = hub.pull("generate-scorecard-questions")

    model = init_chat_model(
        model="gpt-4o-2024-08-06", model_provider="openai", temperature=0
    ).with_structured_output(ListQuestions)

    chain = prompt | model

    res: ListQuestions = chain.invoke(
        {
            "raw_job_posting": state.raw_job_posting,
            "web_context": state.web_context,
        }
    )

    return {"generated_questions": res.questions}
