from pathlib import Path

import pytest

# "The conftest.py file serves as a means of providing fixtures for an entire directory.
# Fixtures defined in a conftest.py can be used by any test in that package without
# needing to import them (pytest will automatically discover them)."
# https://docs.pytest.org/en/latest/reference/fixtures.html


@pytest.fixture
def mock_data_path():
    return Path(__file__).parent.joinpath("mock_data/")


@pytest.fixture
def mock_workflow_database_tsv(mock_data_path):
    return mock_data_path.joinpath("all.workflow.database.tsv")
