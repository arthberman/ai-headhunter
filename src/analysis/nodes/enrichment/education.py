import os
import uuid
from datetime import datetime
from typing import Optional, cast

from langchain import hub
from langchain_community.tools import TavilySearchResults
from langchain_core.runnables import Runnable, RunnableConfig
from sqlalchemy import (
    ARRAY,
    Column,
    DateTime,
    String,
    UniqueConstraint,
    create_engine,
    select,
)
from sqlalchemy.dialects.postgresql import UUID, insert
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from analysis.full.configuration import Configuration
from analysis.full.state import EducationState, MainGraphState
from analysis.models.profile import ProfileEducation
from analysis.models.school import SchoolInfo
from utils import init_model

Base = declarative_base()


class EnrichmentSchool(Base):
    """School enrichment model."""

    __tablename__ = "EnrichmentSchool"
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
    fields = Column(ARRAY(String))
    ranking = Column(String)

    __table_args__ = (
        UniqueConstraint("name", "linkedinUrl", name="uq_school_name_linkedinUrl"),
    )


tavily_tool = TavilySearchResults(
    max_results=10, include_answer=True, search_depth="advanced"
)


def create_db_session():
    """Create a database session."""
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise ValueError("DATABASE_URL environment variable is not set")
    engine = create_engine(database_url)
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal()


def get_school_from_db(
    session: Session, name: str, linkedin_url: str
) -> EnrichmentSchool | None:
    """Get a school from the database."""
    stmt = select(EnrichmentSchool).where(
        (EnrichmentSchool.name == name) & (EnrichmentSchool.linkedinUrl == linkedin_url)
    )
    return session.execute(stmt).scalar_one_or_none()


def add_school_to_db(session: Session, school_info: SchoolInfo) -> None:
    """Add a school to the database or update if it already exists."""
    insert_stmt = insert(EnrichmentSchool).values(
        name=school_info.name,
        description=school_info.description,
        linkedinUrl=school_info.linkedin_url,
        fields=school_info.fields,
        ranking=school_info.ranking,
    )

    do_update_stmt = insert_stmt.on_conflict_do_update(
        index_elements=["name", "linkedinUrl"],
        set_={
            "description": school_info.description,
            "fields": school_info.fields,
            "ranking": school_info.ranking,
            "updatedAt": datetime.now(),
        },
    )

    try:
        session.execute(do_update_stmt)
        session.commit()
    except IntegrityError as e:
        session.rollback()
        raise ValueError(f"IntegrityError occurred while adding/updating school: {e}")


def node_education_enrichment(
    state: EducationState, *, config: Optional[RunnableConfig] = None
) -> MainGraphState:
    """Enrich the education of the candidate."""
    education: ProfileEducation = state["education"]
    db_session = create_db_session()

    try:
        # Load configuration from the provided RunnableConfig
        configuration = Configuration.from_runnable_config(config)

        # Check if the school exists in the database
        db_school = get_school_from_db(
            db_session, education.school, education.linkedin_url
        )

        if db_school:
            return {
                "education_enrichment": [
                    SchoolInfo(
                        name=db_school.name,
                        description=db_school.description,
                        linkedin_url=db_school.linkedinUrl,
                        fields=db_school.fields,
                        ranking=db_school.ranking,
                    )
                ]
            }

        # If not in database, perform Tavily search
        tavily_res = tavily_tool.invoke(
            {"query": f"school {education.school} ({education.linkedin_url})"}
        )
        prompt = hub.pull("generate-education-enrichment:production")

        # Initialize the chat model with the provided configuration
        raw_model = init_model(configuration.enrichment_model)
        model = raw_model.with_structured_output(SchoolInfo)

        chain = cast(Runnable, prompt | model)
        res = cast(
            SchoolInfo,
            chain.invoke(
                {
                    "web_browsing_result": tavily_res,
                    "school": education.school,
                    "school_description": education.description,
                    "linkedin_url": education.linkedin_url,
                }
            ),
        )

        # Add the new school info to the database
        add_school_to_db(db_session, res)

        return {"education_enrichment": [res]}
    finally:
        db_session.close()
