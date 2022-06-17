import shutil
from pathlib import Path

import pytest

# "The conftest.py file serves as a means of providing fixtures for an entire directory.
# Fixtures defined in a conftest.py can be used by any test in that package without
# needing to import them (pytest will automatically discover them)."
# https://docs.pytest.org/en/latest/reference/fixtures.html


@pytest.fixture
def tests_metadata_path():
    return Path(__file__).parents[1].joinpath("metadata/")


@pytest.fixture
def mock_data_path():
    return Path(__file__).parent.joinpath("mock_data/")


@pytest.fixture
def mock_workflow_database_tsv(mock_data_path):
    return mock_data_path.joinpath("all.workflow.database.tsv")


@pytest.fixture
def tmp_submission_file(mock_workflow_database_tsv, tmp_path):
    # Create temporary submission file path
    tmp_submission_file = str(tmp_path) + "/submission_file.text"

    # Copy mock submission file template to temp submission file
    shutil.copyfile(mock_workflow_database_tsv, tmp_submission_file)

    return tmp_submission_file
