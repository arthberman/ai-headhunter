from typing import cast

from langchain import hub
from langchain.chat_models import init_chat_model
from langchain_core.runnables import RunnableLambda
from matcher.state import MainGraphState
from matcher.synthesis.models import ExtendedScoredCriterion, Synthesis
from src.scorecard.models.scorecard import ImportanceLevel


def node_synthesis(state: MainGraphState) -> MainGraphState:
    prompt = hub.pull("analyse-synthesis")
    model = init_chat_model(
        model="claude-3-5-sonnet-20240620", model_provider="anthropic", temperature=0
    )
    chain = cast(RunnableLambda, prompt | model.with_structured_output(Synthesis))

    extended_scored_criterion = []
    for scored_criterion in state.scored_criterion:
        criterion = next(
            (
                c
                for c in state.scorecard.mustHaveCriteria
                + state.scorecard.importantCriteria
                + state.scorecard.niceToHaveCriteria
                if c.id == scored_criterion.id
            ),
            None,
        )
        if criterion:
            extended_scored_criterion.append(
                ExtendedScoredCriterion(
                    **scored_criterion.model_dump(),
                    description=criterion.description,
                    importance_level=(
                        ImportanceLevel.MUST_HAVE
                        if criterion in state.scorecard.mustHaveCriteria
                        else (
                            ImportanceLevel.IMPORTANT
                            if criterion in state.scorecard.importantCriteria
                            else ImportanceLevel.NICE_TO_HAVE
                        )
                    ),
                    criterion_type=criterion.type,
                )
            )

    res = cast(
        Synthesis,
        chain.invoke(
            {
                "profile": state.profile,
                "extended_scored_criterion": extended_scored_criterion,
                "scorecard_synthesis": state.scorecard_synthesis,
            }
        ),
    )

    return {"synthesis": res}
