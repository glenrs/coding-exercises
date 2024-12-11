from dataclasses import dataclass

import factory
from pytest_factoryboy import LazyFixture
from sqlalchemy.ext.declarative import declarative_base

from _data_models import Base
from _dao import ABCDAO


__all__ = "TableFactory",


@dataclass
class Table:
    table_object: declarative_base
    data: list
    column_names: tuple
    

class TableFactory(factory.Factory):
    class Meta:
        model = Table

    table_object: declarative_base = Base
    db_session = LazyFixture("db_session")
    column_names =  LazyFixture
    data = []
    monkeypatch = LazyFixture("monkeypatch")

    @classmethod
    def _create(cls, model_class, table_object, db_session, column_names, data, monkeypatch, *args, **kwargs):
        instance = model_class(
            table_object=table_object, data=data, column_names=column_names,
            *args, **kwargs
        )
        conn = db_session.connection()
        for record in data:
            record_object = table_object.insert().values(**dict(zip(column_names, record)))
            conn.execute(record_object)
        
        monkeypatch.setattr(ABCDAO, "session", db_session)

        return instance