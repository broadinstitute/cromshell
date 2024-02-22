# Development

Welcome to Cromshell's development document, here you will find instructions 
on setting up your environment and other relevant material for contributing to Cromshell. 

## Getting Started
Cromshell development requires python3 (>=.7) to be installed, afterwards 
the Cromshell development environment can be set up by the following steps:

1. Pull cromshell git repository 
```shell
    git clone git@github.com:broadinstitute/cromshell.git
    cd cromshell
    git checkout cromshell_2.0
    git checkout -b <your initial>_<name of your new branch>
```
2. Create a virtual python environment
```shell
    python3 -mvenv venv
    . venv/bin/activate
    pip install --upgrade pip
    pip install -r dev-requirements.txt
    pip install -e . 
```
    
After following the above development environment setup steps, cromshell should 
have been added to your path.
Run `cromshell --help` to confirm installation.

    > cromshell --help
    Usage: cromshell [OPTIONS] COMMAND [ARGS]...
    
      Cromshell is a script for submitting workflows to a cromwell server and
      monitoring / querying their results.


### Setup Cromshell configuration files

If Cromshell determines `~/.cromshell` does not exist it will 
automatically create a hidden directory containing configuration files 
after running on of its sub commands.

1. Run 
```shell
    cromshell-alpha version
```
The following directory and files should be created
```
    > ~/.cromshell
            all.workflow.database.tsv
            cromshell_config.json
```

- all.workflow.database.tsv : Tab-delimited file listing all workflows executed by the user
- cromshell_config.json : Configuration file for cromshell  

2. Edit the `cromshell_config` file so that the desired Cromwell server is being used, for example:
```json
{
  "cromwell_server": "http://localhost:8000",
  "requests_timeout": 5
}
```  
You can set the `"cromwell_server"` to an existing server or create a local one temproraly using a docker container, then setting the config to  `http://localhost:8000` like in the example above. The command below can be used to create a Cromwell version 67 server container. 

```shell
	docker run -d -p 8000:8000 broadinstitute/cromwell:67 server
```

How do these configurations affect your cromshell1.0 configs?  
Cromshell2.0 uses the same all.workflow.database.tsv as cromshell1, thus it will read-write 
to the same file. The cromshell_config.json file is new in cromshell2.0, 
changes to this file will not affect your cromshell1.0 settings.

## Development Steps

Now that you have set up your Cromshell environment, you can start adding and testing
new commands and features. There are three main steps to follow: 

1. [Add a command or feature to the codebase](../developer_docs/addcommand.md) 
2. [Add unit and integration tests for the added scripts](../developer_docs/addtests.md)
3. [Run test and linting scripts](../developer_docs/runtests.md)

Once you have a functional command or feature with all of its unit/integration tests
successfully completing, then you can push your changes to the cromshell branch for review. 

## Best Practices

When styling your code use the following [site](https://peps.python.org/pep-0008/#constants)

- A well formatted function will have 
  - Lower case name with underscores as spaces
  - Use type hint where-ever possible
  - Includes a doc string describing the function and parameters.  
```python

def alias_exists(alias_name: str, submission_file: str) -> bool:
   """
   Check if alias name already exists in submission file
   :param alias_name: Alternate string identifier for workflow submission
   :param submission_file: Path to cromshell submission file
   :return:
   """
   ...
```
- Have a goal to make unit tests for every new function added.

## Versioning

We use `bumpversion` to maintain version numbers.
DO NOT MANUALLY EDIT ANY VERSION NUMBERS.

Our versions are specified by a 3 number semantic version system (https://semver.org/):

	major.minor.patch

To update the version with bumpversion do the following:

`bumpversion PART` where PART is one of:
- major
- minor
- patch

This will increase the corresponding version number by 1.
