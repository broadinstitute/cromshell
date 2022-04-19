# Mock Data

Mock data for Cromshell is stored in the tests directory and refers to any input 
files required for testing. This can be cromwell workflow metadata, 
all.workflows.database.tsv, workflows, cromshell configuration file template, etc.. 
Mock workflows have their own directory under the tests directory. Other types of mock 
data are stored in mock directories in both unit and integration test directories. 
Some mock data are only used by a particular command, in that case, the directory is 
created for that command in the mock directory.


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