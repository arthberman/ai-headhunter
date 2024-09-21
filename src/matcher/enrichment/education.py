import os
from sqlalchemy import create_engine, ARRAY, Column, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Session, sessionmaker, declarative_base
from langchain import hub
from langchain.chat_models import init_chat_model
from sqlalchemy import select
import uuid

from matcher.models.profile import ProfileEducation
from matcher.models.school import SchoolInfo
from matcher.state import MainGraphState, EducationState
from langchain_community.tools import TavilySearchResults

Base = declarative_base()


class EnrichmentSchool(Base):
    __tablename__ = "EnrichmentSchool"
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    name = Column(String, nullable=False)
    description = Column(String)
    linkedinUrl = Column(String, nullable=False)
    fields = Column(ARRAY(String))
    ranking = Column(String)


tavily_tool = TavilySearchResults(max_results=3)


def create_db_session():
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
    stmt = select(EnrichmentSchool).where(
        (EnrichmentSchool.name == name) & (EnrichmentSchool.linkedinUrl == linkedin_url)
    )
    return session.execute(stmt).scalar_one_or_none()


def add_school_to_db(session: Session, school_info: SchoolInfo) -> None:
    new_school = EnrichmentSchool(
        name=school_info.name,
        description=school_info.description,
        linkedinUrl=school_info.linkedin_url,
        fields=school_info.fields,
        ranking=school_info.ranking,
    )
    session.add(new_school)
    session.commit()


def node_education_enrichment(state: EducationState) -> MainGraphState:
    education: ProfileEducation = state["education"]
    db_session = create_db_session()

    try:
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
                        uncertainty=False,
                    )
                ]
            }

        # If not in database, perform Tavily search
        tavily_res = tavily_tool.invoke({"query": f"school {education.school}"})
        prompt = hub.pull("education-enrichment")
        model = init_chat_model(
            model="gpt-4o-mini", model_provider="openai", temperature=0
        ).with_structured_output(SchoolInfo)
        chain = prompt | model
        res: SchoolInfo = chain.invoke(
            {
                "web_browsing_result": tavily_res,
                "school": education.school,
                "school_description": education.description,
                "linkedin_url": education.linkedin_url,
            }
        )

        # Add the new school info to the database
        add_school_to_db(db_session, res)

        return {"education_enrichment": [res]}
    finally:
        db_session.close()
