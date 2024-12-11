from sqlalchemy import INTEGER, Column, ForeignKey
from sqlalchemy.types import VARCHAR, TIMESTAMP, BOOLEAN
from sqlalchemy.dialects.postgresql import UUID

from .base import DataModelBase, Base


__all__ = "CompaniesDim",


class CompaniesDim(DataModelBase, Base):
    __tablename__ = "companies_dim"

    ID = Column("id", UUID, primary_key=True)
    Domain = Column("domain", VARCHAR, nullable=False)