from dotenv import load_dotenv
import os
from typing import List
from datetime import datetime
from enum import Enum as PyEnum
from uuid import UUID

from sqlalchemy import create_engine, Column, String, DateTime, Enum
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.dialects.postgresql import UUID as sqlUUID
from sqlalchemy.sql import func

from matcher.models.knowledge_point import KnowledgePoint
from scorecard.models.scorecard import CriteriaType

load_dotenv()

Base = declarative_base()


class KnowledgePointORM(Base):
    __tablename__ = "KnowledgePoint"

    id = Column(
        sqlUUID(as_uuid=True), primary_key=True, server_default=func.uuid_generate_v4()
    )
    createdAt = Column(DateTime, server_default=func.now())
    updatedAt = Column(DateTime, server_default=func.now(), onupdate=func.now())
    type = Column(Enum(CriteriaType))
    description = Column(String)


class KnowledgePointDatabase:
    def __init__(self):
        self.connection_string = os.getenv("DATABASE_URL")
        self.engine = create_engine(self.connection_string)
        self.Session = sessionmaker(bind=self.engine)

    def get_knowledge_points(
        self, types: List[str] = None, limit: int = 50
    ) -> List[KnowledgePoint]:
        session = self.Session()
        query = session.query(KnowledgePointORM)

        if types:
            query = query.filter(KnowledgePointORM.type.in_(types))

        results = query.limit(limit).all()
        session.close()

        # Convert ORM objects to simplified Pydantic models
        return [
            KnowledgePoint(description=result.description, type=result.type.value)
            for result in results
        ]

    def get_all_knowledge_points(self) -> List[KnowledgePoint]:
        session = self.Session()
        results = session.query(KnowledgePointORM).all()
        session.close()

        # Convert ORM objects to simplified Pydantic models
        return [
            KnowledgePoint(description=result.description, type=result.type.value)
            for result in results
        ]


db = KnowledgePointDatabase()


def get_knowledge_points(types: List[str]) -> List[KnowledgePoint]:
    """Query the knowledge point database for information related to the given types."""
    return db.get_knowledge_points(types=types)
