import os
from pathlib import Path

import pytest

# "The conftest.py file serves as a means of providing fixtures for an entire directory.
# Fixtures defined in a conftest.py can be used by any test in that package without
# needing to import them (pytest will automatically discover them)."
# https://docs.pytest.org/en/latest/reference/fixtures.html


@pytest.fixture
def local_cromwell_url():
    return "http://localhost:8000"


@pytest.fixture  # Env variable set in tox.ini
def local_hidden_cromshell_folder():
    return Path(os.environ.get("CROMSHELL_CONFIG")).joinpath(".cromshell")


@pytest.fixture
def local_workflow_database_tsv(local_hidden_cromshell_folder):
    return Path(local_hidden_cromshell_folder).joinpath("all.workflow.database.tsv")


@pytest.fixture
def local_cromshell_config_json(local_hidden_cromshell_folder):
    return Path(local_hidden_cromshell_folder).joinpath("cromshell_config.json")


@pytest.fixture
def test_workflows_path():
    return Path(__file__).joinpath("workflows/")


@pytest.fixture
def get_current_version() -> str:
    filename = Path(__file__).parents[1].joinpath("src/cromshell/__main__.py")
    with open(filename) as f:
        for line in f:
            if line.startswith("__version__"):
                version = line.split("=")[1].strip().strip('"')

    return version
