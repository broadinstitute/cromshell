import re
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

@pytest.fixture
def workflows_path():
    return Path(__file__).parents[1].joinpath("workflows/")

@pytest.fixture
def ansi_escape():
    """
    Removes ansi formatting from string. Useful when needing to remove
    font or color formatting from a printout making assertions easier.
    https://stackoverflow.com/questions/14693701
    :return:
    """
    return re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")


@pytest.fixture
def local_cromwell_url():
    return "http://localhost:8000"
