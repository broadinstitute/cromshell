# Mock Data

Mock data for Cromshell is stored in the tests directory and refers to any input 
files required for testing. This can be cromwell workflow metadata, 
all.workflows.database.tsv, workflows, cromshell configuration file template, etc.. 
Mock workflows have their own directory under the tests directory. Other types of mock 
data are stored in mock directories in both unit and integration test directories. 
Some mock data are only used by a particular command, in that case, the directory is 
created for that command in the mock directory.

```
> tests
    > integration
       > mock
           all.workflow.database.tsv
    > unit
       > mock
           > submit
               submission_file_template.text
           all.workflow.database.tsv
           cromshell_config.json           
    > workflows
        helloWorld.json
        helloWorld.wdl
    __init__.py
    conftest.py 
```

As an example, the `status` command has a few functions that needs metadata to process. 
Thus, tests functions created for this command will require access to mock metadata. In
the example below the `test_workflow_failed_for_metadata_that_is_doomed` test function
is given the path to the mock data directory by the `mock_data_path` pytest fixture. The
test function then selects a specific mock metadata to use for its assertion, in this 
case the `doom_workflow_slim_metadata.json`. 


```python
import json
import os

import pytest

from cromshell.status import command as status_command


class TestStatus:
    """Test the status command functions"""

    def test_workflow_failed_for_metadata_that_is_doomed(self, mock_data_path):
        workflow_metadata_path = os.path.join(
            mock_data_path, "doom_workflow_slim_metadata.json"
        )
        with open(workflow_metadata_path, "r") as f:
            workflow_metadata = json.load(f)

        assert status_command.workflow_failed(workflow_metadata) is True, (
            "A running doomed workflow metadata should have "
            "output 'True' to indicate workflow "
            "has failed."
        )

    @pytest.fixture
    def mock_data_path(self):
        return os.path.join(os.path.dirname(__file__), "mock_data/")
```

This is a very direct way of accessing the
mock data directory, because of some updates to the `tests` folder your test script 
shouldn't need to create its own pytest fixture for obtaining the mock data directory. 
Instead try to look for these type of generic fixtures in the [`../tests/conftest.py`](../tests/conftest.py) 
or the `../tests/<unit/integration>/conftest.py` directories. If you find one then it
is possible to directly use the pytest fixture without needing to import the conftest.py
file, this handled by pytest in the background (More on conftest.py [here](https://docs.pytest.org/en/6.2.x/fixture.html))
The example below uses the `mock_data_path` fixture from `../tests/unit/conftest.py` instead 
of creating its own. 

```python
import json
import os

from cromshell.status import command as status_command


class TestStatus:
    """Test the status command functions"""

    def test_workflow_failed_for_metadata_that_is_doomed(self, mock_data_path):
        workflow_metadata_path = os.path.join(
            mock_data_path, "doom_workflow_slim_metadata.json"
        )
        with open(workflow_metadata_path, "r") as f:
            workflow_metadata = json.load(f)

        assert status_command.workflow_failed(workflow_metadata) is True, (
            "A running doomed workflow metadata should have "
            "output 'True' to indicate workflow "
            "has failed."
        )
```