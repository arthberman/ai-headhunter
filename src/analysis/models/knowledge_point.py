import uuid
from datetime import datetime

from pydantic import BaseModel, Field
from sqlalchemy import Column, DateTime, Enum, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base

from scorecard.models.scorecard import CriterionType


class KnowledgePoint(BaseModel):
    """Knowledge point model."""

    description: str = Field(description="The description of the knowledge point")
    type: str = Field(description="Type of this knowledge point")


Base = declarative_base()


class KnowledgePointDB(Base):
    """Knowledge point database model."""

    __tablename__ = "KnowledgePoint"
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
    type = Column(Enum(CriterionType), nullable=False)
    description = Column(String, nullable=False)
