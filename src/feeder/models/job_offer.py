from pydantic import BaseModel


class JobOfferDescription(BaseModel):
    summary: str
    seniority: str
    location: str

    @property
    def job_description(self) -> str:
        return self.summary

    @property
    def job_location(self) -> str:
        return self.location

    @property
    def job_seniority(self) -> str:
        return self.seniority
