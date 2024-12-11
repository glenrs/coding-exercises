from abc import ABC, abstractproperty
from dataclasses import dataclass
from functools import cached_property

from sqlalchemy import create_engine
from sqlalchemy.orm.session import sessionmaker

import uuid

from _base import Session


__all__ = "ABCDAO",


@dataclass
class ABCDAO(ABC):

    @cached_property
    def session(self):
        return Session().session
    
    @abstractproperty
    def table_class(self):
        """Class type of table"""
    
    @property
    def query(self):
        return self.session.query(self.table_class)

    def write(self, **kwargs):
        """Default for fact tables"""
        record_id = str(uuid.uuid4())
        self.session.add(
            self.table_class(
                ID=record_id,
                **kwargs
            )
        )
        self.session.commit()
        return record_id
    
    def update(self, record, **kwargs):
        for k,v in kwargs.items():
            setattr(record, k, v)
        self.session.commit()
        return record