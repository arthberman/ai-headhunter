from langchain import hub
from langchain.chat_models import init_chat_model
from langchain_core.prompts import ChatPromptTemplate

from matcher.models.job_offer import JobOffer
from matcher.models.scorecard import Scorecard


""" def parseScorecard(job_offer: JobOffer) -> Scorecard:
    model = init_chat_model(
        model="gpt-4o-2024-08-06", model_provider="openai", temperature=0
    )
    structured_model = model.with_structured_output(Scorecard)
    prompt = hub.pull("parser-scorecard")

    chain = prompt | model
    output = chain.invoke(job_offer)

    prompt_template = ChatPromptTemplate.from_messages(
        [
            ("system", "Please structure the following input as a Scorecard object"),
            (
                "user",
                "Input: {rawScorecard}",
            ),
        ]
    )

    chain_structured = prompt_template | structured_model

    structured_output = chain_structured.invoke({"rawScorecard": output})
    return structured_output
 """

def parseScorecard(job_offer: JobOffer) -> Scorecard:
    model = init_chat_model(
        model="gpt-4o-2024-08-06", model_provider="openai", temperature=0
    )
    structured_model = model.with_structured_output(Scorecard)
    prompt = hub.pull("parser-scorecard")

    chain = prompt | structured_model
    output = chain.invoke(job_offer)

    return output