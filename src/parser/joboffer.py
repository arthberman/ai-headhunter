from langchain import hub
from langchain.chat_models import init_chat_model

from matcher.models.job_offer import JobOffer


def parseJobOffer(jobOffer: str) -> JobOffer:
    model = init_chat_model(
        model="gpt-4o-2024-08-06", model_provider="openai", temperature=0
    )
    structured_model = model.with_structured_output(JobOffer)
    prompt = hub.pull("joboffer-parser")

    chain = prompt | structured_model
    output = chain.invoke(jobOffer)
    return output