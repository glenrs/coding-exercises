import pytest


@pytest.fixture
def companies_dim__column_names():
    return ["id",  "domain"]


@pytest.fixture
def companies_dim__data():
    return []


@pytest.fixture
def company_entities_dim__column_names():
    return ["id",  "company_id", "name"]


@pytest.fixture
def company_entities_dim__data():
    return []


@pytest.fixture
def completions_fact__column_names():
    return ["id",  "prompt_id", "context", "raw_output", "normalized_output"]


@pytest.fixture
def completions_fact__data():
    return []


@pytest.fixture
def contacts_dim__column_names():
    return ["id",  "company_id", "name", "title", "email"]


@pytest.fixture
def contacts_dim__data():
    return []


@pytest.fixture
def dq_completion_fact__column_names():
    return ["id",  "completion_id", "type", "result"]


@pytest.fixture
def dq_completion_fact__data():
    return []


@pytest.fixture
def prompt_config__column_names():
    return ["id",  "name", "model", "version", "system_instructions", "json_validation"]


@pytest.fixture
def prompt_config__data():
    return []
