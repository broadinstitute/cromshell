# Add Unit and Integration Tests

Test are essential to having a stable code base, Cromshell uses both automated Unit and 
Integration tests executed for every Git push. Unit tests normally test individual 
functions in Cromshell while Integration tests will test the functionality of large 
segments of the tool such as a subcommand. This document will cover the process
of adding tests for a new Cromshell subcommand. 

All tests for Cromshell are within the `tests` directory:
```
> tests
    > integration
    > unit
    > workflows
    __init__.py
    conftest.py 
```
- **integration**: Contains integration tests, this is where you will add your integration test
- **unit** : Contains unit tests, this where you will add your unit test
- workflows : Mock workflows used for testing 
- conftest.py : Holds utility pytest fixtures which can be used by unit and integrations tests. Both the unit and integration directory have their own conftest.py, functions fixtures within those files are only accessible by their respective test type. More about conftest [here](https://docs.pytest.org/en/6.2.x/fixture.html)

**Important Note: As you create tests in the next sections it is important to follow the naming 
conventions listed below when creating files, classes, and functions. 
It allows the testing tools Tox and Pytest to identify which files should be tested.** 
- **Names of test files begin with 'test'**
- **Names of classes containing tests begin with 'Test'**  
- **Names of functions to be run as tests begin with 'test'**  

### Install Testing Dependencies
There are some test specific python packages that will need to be installed using 
the command below.
```shell
pip install -r dev-requirements.txt
```
### Add Unit tests

Begin by creating a file under the unit test directory having a name starting 
with `test_` followed by the name of your command. 

```
> tests
    > unit
       conftest.py
       **test_my_new_command.py**
       test_commanda.py
       test_commandb.py
```

Assuming the function below is located in a command called `my_new_command`, 
```python
def get_hello_world():
    return "hello world"
```

the following script would be an example of the contents of a unit test 
file for the function.  
```python
import pytest

from cromshell.my_new_command import command as my_new_command


class TestMyNewCommand:
    
    """Tests for my_new_command """

    # First Test
    def test_get_hello_world(self):

        y = "hello world"

        assert my_new_command.get_hello_world() == y
    
    # Second Test
    @pytest.mark.parametrize(        
        "y",
        [
            ("wombat"),
            ("foo"),
            ("Failed"),
        ],
    )
    def test_get_hello_world_using_parametrize(self, y: str):

        y = "hello world"

        assert my_new_command.get_hello_world() != y
```

There are some key things to note in the template above:
- Pytest is imported to use pytest features such as parametrizing a test function, 
and creating and importing fixtures. 
- The command being tested is also imported to give us access to the functions to test. 
- A class is created to house all tests functions, the name of the class will need to 
start with “Test” followed by the name of the command in camelcase.
- The test function names should be labeled with the name of the function to be tested, 
and sometimes an additional description in the name to help distinguish functions with 
more than one test. (e.g. test_format_metadata_params_**subworkflows_flag** and 
test_format_metadata_params_**exclude_keys_flag**)
- The second function in the template above shows an example of the pytest parametrize 
feature, refer to the [docs](https://docs.pytest.org/en/6.2.x/parametrize.html) for details

Note:
- You may need mock data for your tests, refer to [mockdata.md](../developer_docs/mockdata.md)
- You may to run the tests while your developing them, the instructions are in [runtests.md](../developer_docs/runtests.md) 

### Add Integration tests

Begin by creating a file under the integration test directory having a name starting 
with `test_` followed by the name of your command. 
```
    > tests
        > integration
           conftest.py
           **test_my_new_command.py**
           test_commanda.py
           test_commandb.py
           utility_test_functions.py
```

Below is an example of the contents of an integration test file. 

```python
import pytest

from tests.integration import utility_test_functions

class TestMyNewCommand:
    
    """Tests for my_new_command """

    def test_my_new_command(self):
        workflow_id = "639b81f9-414e-4c65-8dcf-bf7c57ffdff7"
        # Run cromshell alias
        results = utility_test_functions.run_cromshell_command(
            command=[
                "my-new-command",
                workflow_id,
            ],
            exit_code=0,
        )
        assert results.stdout == workflow_id
```

As you can see, formatting for integration tests is very similar to the unit tests, 
the major things to note are:
- Instead of importing the command module to be tested, a test utility function is imported
- The utility function run_cromshell_command is the easiest way to test a cromshell 
command. Provided the command and arguments being tested the function will assert that 
the command ends with the provided exit code. The function will also return the results 
of execution for further testing. 

