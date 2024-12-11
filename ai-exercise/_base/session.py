from abc import ABC
from dataclasses import dataclass
from functools import cached_property

from sqlalchemy import create_engine
from sqlalchemy.orm.session import sessionmaker

from .base import Base


__all__ = "Session",


@dataclass
class Session(Base):
    def __new__(cls):
        """sets up Session as a singleton."""
        if not hasattr(cls, 'instance'):
            cls.instance = super(Session, cls).__new__(cls)
        return cls.instance

    @cached_property
    def engine(self):
        db_context = self.context.db_context
        connection_str = f"postgresql+psycopg2://{db_context.user}:{db_context.password}@{db_context.host}:{db_context.port}/{db_context.db}"
        return create_engine(connection_str)

    def _setup(self, session):
        """This is a handler for testing to override and create tables"""

    def _teardown(self, session, con):
        """This is a handler for testing to override and rollback"""
        session.commit()
        session.close()

    def _create_session(self):
        with self.engine.connect() as con:
            session = sessionmaker(
                bind=self.engine, # .execution_options(schema_translate_map={'dynamic':self.context.schema})
                expire_on_commit=False
            )()
            self._setup(session)
            yield session
            self._teardown(session, con)

    @cached_property
    def session(self):
        return next(self._create_session())