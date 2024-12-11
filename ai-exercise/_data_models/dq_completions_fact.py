from sqlalchemy import INTEGER, Column, ForeignKey
from sqlalchemy.types import VARCHAR, TIMESTAMP, BOOLEAN
from sqlalchemy.dialects.postgresql import UUID

from .base import DataModelBase, Base
from .completions_fact import CompletionsFact


__all__ = "DQCompletionsFact",


class DQCompletionsFact(DataModelBase, Base):
    __tablename__ = "dq_completion_fact"

    ID = Column("id", UUID, primary_key=True)
    CompletionID = Column("completion_id", UUID, ForeignKey(CompletionsFact.ID), nullable=False)
    Type = Column("type", VARCHAR, nullable=False) # TODO: update to 
    Result = Column("result", VARCHAR, nullable=False)