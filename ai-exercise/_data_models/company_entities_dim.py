from sqlalchemy import INTEGER, Column, ForeignKey
from sqlalchemy.types import VARCHAR, TIMESTAMP, BOOLEAN
from sqlalchemy.dialects.postgresql import UUID

from .base import DataModelBase, Base
from .companies_dim import CompaniesDim


__all__ = "CompanyEntitiesDim",


class CompanyEntitiesDim(DataModelBase, Base):
    __tablename__ = "company_entities_dim"

    ID = Column("id", UUID, primary_key=True)
    CompanyId = Column("company_id", UUID, ForeignKey(CompaniesDim.ID), nullable=False)
    Name = Column("name", VARCHAR, nullable=False)