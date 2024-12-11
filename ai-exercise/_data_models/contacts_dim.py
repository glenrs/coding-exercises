from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.types import VARCHAR

from .base import Base, DataModelBase 
from .companies_dim import CompaniesDim


__all__ = "ContactsDim",


class ContactsDim(DataModelBase, Base):
    __tablename__ = 'contacts_dim'

    ID = Column("id", UUID, primary_key=True)
    CompanyId = Column("company_id", UUID, ForeignKey(CompaniesDim.ID), nullable=True)
    Name = Column("name", VARCHAR, nullable=False)
    Title = Column("title", VARCHAR, nullable=False)
    Email = Column("email", VARCHAR, nullable=False)
    Phone = Column("phone", VARCHAR, nullable=False)
    # Address = Column("address", VARCHAR, nullable=False)

