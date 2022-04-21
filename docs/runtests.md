# Running Tests

This document demonstrates how to run Cromshell's tests. All tests can be run from the 
Cromshell directory. 

### Linting files

As a reminder, linter is used to scan your code for styling corrections and issues that 
may lead to bugs. The main method linting can be executed is through Tox, which will
run all the linting tools. However, It's possible to run the linting tools individually
as seen below

    # run all linting commands
    tox -e lint

    # reformat all project files
    black src tests setup.py

    # sort imports in project files
    isort -rc src tests setup.py

    # check pep8 against all project files
    flake8 src tests setup.py

    # lint python code for common errors and codestyle issues
    pylint src

### Running Tests

To run tests in the `/tests` directory use the Tox commands below.

    # run all linting and test
    tox

    # run only unit tests
    tox -e unit

    # run only integration tests 
    tox -e integration

    # run only linting
    tox -e lint

**Integration Testing**  
Running integration tests isn't as simple as running unit tests. Some integration 
tests (e.g. submit command) are running Cromshell in a way that will require access to
a local Cromwell server and will fail unless it finds a server. This can be easily 
remedied by running a containerized local cromshell server with the following command:

    docker run -p 8000:8000 broadinstitute/cromwell:67 server

