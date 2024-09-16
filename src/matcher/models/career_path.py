from pydantic import BaseModel, Field


class CareerPathAnalysis(BaseModel):
    explanationSeniority: str = Field(
        ...,
        description="Detailed explanation of the seniority assessment, comparing the candidate's years of relevant experience with the job requirements. Limited to 250 characters.",
    )

    explanationHierarchy: str = Field(
        ...,
        description="Detailed explanation of the hierarchy assessment, evaluating changes in organizational level or scope of responsibility. Limited to 250 characters.",
    )

    explanationPrestige: str = Field(
        ...,
        description="Detailed explanation of the prestige assessment, comparing the reputation of the current and offered companies. Limited to 250 characters.",
    )

    explanationIntent: str = Field(
        ...,
        description="Detailed explanation of the intent to move assessment, evaluating the likelihood of the candidate changing jobs based on recent career history. Limited to 250 characters.",
    )

    scoreSeniority: int = Field(
        ...,
        description="Score (0 or 1) indicating whether the candidate's seniority level is suitable for the job offer. 1 if their experience meets or exceeds requirements, 0 if significantly under-qualified.",
    )

    scoreHierarchy: int = Field(
        ...,
        description="Score (0 or 1) indicating whether the hierarchical move is suitable. 1 for lateral moves or promotions, 0 for significant step-downs in organizational level.",
    )

    scorePrestige: int = Field(
        ...,
        description="Score (0 or 1) indicating whether the move in terms of company prestige is suitable. 1 if moving to an equally or more prestigious company, 0 if moving to a significantly less prestigious company.",
    )

    scoreIntent: int = Field(
        ...,
        description="Score (0 or 1) indicating the likelihood of the candidate's intent to move. 1 if the candidate is likely to consider a move, 0 if recent changes suggest they're unlikely to move.",
    )
