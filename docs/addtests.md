# Add Unit and Integration Tests

Test are essential to having a stable code base, cromshell uses both Unit and Integration tests. 
Unit tests normally test individual functions in cromshell while Integration tests will test the functionality of large segments of the code base such as a whole command. All tests for Cromshell are within the test diretory:

    > tests
        > integration
        > unit
        > workflows
        __init__.py
        conftest.py 

- integration: Contains integration tests (where you add your test)
- unit : Contains unit tests (where you add your test)
- workflows : Mock workflows used for testing 
- conftest.py : Holds utility pytest fixtures which can be used by unit and integrations tests. Both the unit and integration directory have their own conftest.py, functions fixtures within those files are only accessible by their respective test type. More about conftest [here](https://docs.pytest.org/en/6.2.x/fixture.html)

#### Add Unit tests

Begin by creating file under the unit test directory starting with “test_” followed by the name of your command. 

Note: Naming is important when creating files, classes, and functions to be tested. It allows the testing tools Tox and Pytest to identify which files should be tested. Be sure to follow the naming formatting in the directions below.
- Names of test files begin with 'test'
- Names of classes containing tests begin with 'Test'
- Names of functions to be run as tests begin with 'test'


    > tests
        > unit
           conftest.py
           **test_my_new_command.py**
           test_commanda.py
           test_commandb.py


Use the following template for the newly created test file. 

    import pytest
    
    from cromshell.my_new_command import command as my_new_command
    
    
    class TestMyNewCommand:
        
        """Tests for my_new_command """
    
        def test_command_function_name(self):
    
            y = "hello world"
    
            assert my_new_command.command_function_name() == y
    
        @pytest.mark.parametrize(        
            "y",
            [
                ("wombat"),
                ("foo"),
                ("Failed"),
            ],
        )
        def test_command_function_name_using_parametrize(self, y: str):
    
            y = "hello world"
    
            assert my_new_command.command_function_name() != y


There are some key things to note in the template above:
- Pytest is imported to use pytest test features such as parametrizing a test function, and creating and importing fixtures. 
- The command to be tested is also imported to be used in testing individual functions in the command. 
- A Class is created to house all tests functions, the name starting with “Test” followed by the name of the command in camelcase.
- The test function names should be labeled with the name of the function to be tested, and sometimes an additional description in the name to help distinguish functions with more than one test. (e.g. ​​test_format_metadata_params_subworkflows_flag and test_format_metadata_params_exclude_keys_flag)
- The second function in the template above shows an example of using pytest parametrize feature, refer to the [docs](https://docs.pytest.org/en/6.2.x/parametrize.html) for details

#### Add Integration tests

Begin by creating file under the integration test directory starting with “test_” followed by the name of your command. 

Note: Naming is important when creating files, classes, and functions to be tested. It allows the testing tools Tox and Pytest to identify which files should be tested. Be sure to follow the naming formatting in the directions below.
- Names of test files begin with 'test'
- Names of classes containing tests begin with 'Test'
- Names of functions to be run as tests begin with 'test'


    > tests
        > integration
           conftest.py
           test_my_new_command.py
           test_commanda.py
           test_commandb.py
           utility_test_functions.py


Use the following template to fill the contents of the new test file. 


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
            assert results.stdout = workflow_id

        


As you can see formatting for integration tests is very similar to the unit tests, the major things to note are:
- Instead of importing the command module to be tested, a test utility function is imported
- The utility function run_cromshell_command is the easiest way to test a cromshell command. Provided the command and arguments being tested the function will assert that the command ends with the provided exit code. The function will also return the results of execution for further testing. 


Note:
- You may need mock data for your tests, refer to [mockdata.md](../docs/mockdata.md)
