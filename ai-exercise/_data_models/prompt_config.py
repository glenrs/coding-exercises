from sqlalchemy import INTEGER, Column, ForeignKey
from sqlalchemy.types import VARCHAR, TIMESTAMP, BOOLEAN
from sqlalchemy.dialects.postgresql import UUID

from .base import DataModelBase, Base


__all__ = "PromptConfig",


# TODO: Migrate to Model Management
class PromptConfig(DataModelBase, Base):
    __tablename__ = "prompt_config" 

    ID = Column("id", UUID, primary_key=True)
    Name = Column("name", VARCHAR, nullable=True)
    Model = Column("model", VARCHAR, nullable=True)
    Version = Column("version", INTEGER, nullable=True)
    SystemInstructions = Column("system_instructions", VARCHAR, nullable=False)
    JsonValidation = Column("json_validation", VARCHAR, nullable=False)
