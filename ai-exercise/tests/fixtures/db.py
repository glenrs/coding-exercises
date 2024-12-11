import pytest
from pytest_postgresql import factories
from pytest_postgresql.janitor import DatabaseJanitor
from sqlalchemy.schema import CreateSchema, DropSchema
from sqlalchemy import text

from _data_models import Base
from _base import Session
from _dao import ABCDAO


test_db_credentials = factories.postgresql_proc(port=None, dbname="test_db")
postgresql = factories.postgresql('test_db_credentials')


@pytest.fixture(scope="function")
def db_session(monkeypatch, test_db_credentials, postgresql):

    def override_test_credentials(s):
        s.context.db_context.user = test_db_credentials.user
        s.context.db_context.password = test_db_credentials.password
        s.context.db_context.host = test_db_credentials.host
        s.context.db_context.port = test_db_credentials.port
        s.context.db_context.db = test_db_credentials.dbname
        return s

    def _setup(self, session):
        try:
            con = session.connection()
            Base.metadata.drop_all(bind=con)
        except: # TODO: fix this try/except. Weird edge case..
            session.rollback()
            con = session.connection()
            Base.metadata.drop_all(bind=con)
        Base.metadata.create_all(bind=con)
    
    def _teardown(self, session, con):
        session.rollback()
        session.close()

    @property
    def _session(self):
        yield from self._create_session()
    
    monkeypatch.setattr(Session, "_setup", _setup)
    monkeypatch.setattr(Session, "_teardown", _teardown)
    monkeypatch.setattr(Session, "session", _session)

    s = Session()
    s = override_test_credentials(s)
    yield from s.session
