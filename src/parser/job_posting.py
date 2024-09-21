from langchain import hub
from langchain.chat_models import init_chat_model

from candidate_matcher.models.job_posting import JobPosting


def parse_job_posting(jobOffer: str) -> JobPosting:
    model = init_chat_model(
        model="gpt-4o-2024-08-06", model_provider="openai", temperature=0
    )
    structured_model = model.with_structured_output(JobPosting)
    prompt = hub.pull("parser-job-posting")

    chain = prompt | structured_model
    output = chain.invoke(jobOffer)
    return output
