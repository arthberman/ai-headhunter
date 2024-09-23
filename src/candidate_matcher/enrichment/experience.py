import os
import uuid
from datetime import datetime
from typing import Optional, cast

from langchain import hub
from langchain_community.tools import TavilySearchResults
from langchain_core.runnables import Runnable, RunnableConfig
from sqlalchemy import ARRAY, Column, DateTime, String, create_engine, select
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from candidate_matcher.configuration import Configuration
from candidate_matcher.models.company import CompanyInfo
from candidate_matcher.models.profile import ProfileExperience
from candidate_matcher.state import ExperienceState, MainGraphState
from candidate_matcher.utils import init_model

Base = declarative_base()


class EnrichmentCompany(Base):
    """Company enrichment model."""

    __tablename__ = "EnrichmentCompany"
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    createdAt = Column(DateTime, nullable=False, default=datetime.now)
    updatedAt = Column(
        DateTime, nullable=False, default=datetime.now, onupdate=datetime.now
    )
    name = Column(String, nullable=False)
    description = Column(String)
    linkedinUrl = Column(String, nullable=False)
    sectors = Column(ARRAY(String))
    companyStage = Column(String)


tavily_tool = TavilySearchResults(max_results=3)


def create_db_session():
    """Create a database session."""
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise ValueError("DATABASE_URL environment variable is not set")
    engine = create_engine(database_url)
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal()


def get_company_from_db(
    session: Session, name: str, linkedin_url: str
) -> EnrichmentCompany | None:
    """Get a company from the database."""
    stmt = select(EnrichmentCompany).where(
        (EnrichmentCompany.name == name)
        & (EnrichmentCompany.linkedinUrl == linkedin_url)
    )
    return session.execute(stmt).scalar_one_or_none()


def add_company_to_db(session: Session, company_info: CompanyInfo) -> None:
    """Add a company to the database."""
    new_company = EnrichmentCompany(
        name=company_info.name,
        description=company_info.description,
        linkedinUrl=company_info.linkedin_url,
        sectors=company_info.sectors,
        companyStage=company_info.company_stage,
    )
    session.add(new_company)
    session.commit()


def node_experience_enrichment(
    state: ExperienceState, *, config: Optional[RunnableConfig] = None
) -> MainGraphState:
    """Enrich the experience of the candidate."""
    experience: ProfileExperience = state["experience"]
    db_session = create_db_session()

    try:
        # Load configuration from the provided RunnableConfig
        configuration = Configuration.from_runnable_config(config)

        # Check if the company exists in the database
        db_company = get_company_from_db(
            db_session, experience.company, experience.linkedin_url
        )

        if db_company:
            return {
                "experience_enrichment": [
                    CompanyInfo(
                        name=db_company.name,
                        description=db_company.description,
                        linkedin_url=db_company.linkedinUrl,
                        sectors=db_company.sectors,
                        company_stage=db_company.companyStage,
                        uncertainty=False,
                    )
                ]
            }

        # If not in database, perform Tavily search
        tavily_res = tavily_tool.invoke({"query": f"company {experience.company}"})
        prompt = hub.pull("generate-experience-enrichment")

        # Initialize the chat model with the provided configuration
        raw_model = init_model(configuration.enrichment_model)
        model = raw_model.with_structured_output(CompanyInfo)

        chain = cast(Runnable, prompt | model)
        res = cast(
            CompanyInfo,
            chain.invoke(
                {
                    "web_browsing_result": tavily_res,
                    "company": experience.company,
                    "company_title": experience.title,
                    "company_description": experience.description,
                    "linkedin_url": experience.linkedin_url,
                }
            ),
        )

        # Add the new company info to the database
        add_company_to_db(db_session, res)

        return {"experience_enrichment": [res]}
    finally:
        db_session.close()
