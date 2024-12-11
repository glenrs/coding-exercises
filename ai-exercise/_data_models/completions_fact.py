from sqlalchemy import INTEGER, Column, ForeignKey
from sqlalchemy.types import VARCHAR, TIMESTAMP, BOOLEAN
from sqlalchemy.dialects.postgresql import UUID

from .base import DataModelBase, Base
from .prompt_config import PromptConfig


__all__ = "CompletionsFact",


class CompletionsFact(DataModelBase, Base):
    __tablename__ = "completions_fact"

    ID = Column("id", UUID, primary_key=True)
    PromptId = Column("prompt_id", UUID, ForeignKey(PromptConfig.ID), nullable=False)
    Context = Column("context", VARCHAR, nullable=False)
    RawOutput = Column("raw_output", VARCHAR, nullable=False)
    NormalizedOutput = Column("normalized_output", VARCHAR, nullable=False)