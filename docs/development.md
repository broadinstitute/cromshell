# Development

Welcome to Cromshell's development document, here you will find instructions 
on setting up your environment and other relevant material for contributing to Cromshell. 

## Getting Started
Cromshell development requires python3 (>=.7) to be installed, afterwards 
the Cromshell development environment can be set up by the following steps:

1. Pull cromshell git repository 
```
    git clone git@github.com:broadinstitute/cromshell.git
    cd cromshell
    git checkout cromshell_2.0
```
2. Create a virtual python environment
```
    python3 -mvenv venv
    . venv/bin/activate
    pip install -r dev-requirements.txt
    pip install -e .
```
    
### Running Development Builds of Cromshell

After following the above development environment setup steps, cromshell should 
have been added to your path.
Run `cromshell-alpha --help` to confirm installation.

    > cromshell-alpha --help
    Usage: cromshell-alpha [OPTIONS] COMMAND [ARGS]...
    
      Cromshell is a script for submitting workflows to a cromwell server and
      monitoring / querying their results.


### Setup Cromshell configuration files

If Cromshell determines `~/.cromshell` does not exist it will 
automatically create a hidden directory containing configuration files 
after running on of its sub commands.

Run 

    cromshell-alpha version

The following directory and files should be created

    > ~/.cromshell
            all.workflow.database.tsv
            cromshell_config.json


- all.workflow.database.tsv : Tab-delimited file listing all workflows executed by the user
- cromshell_config.json : Configuration file for cromshell  

Edit the cromshell_config file so that the proper Cromwell server is being used, for example:


    {
      "cromwell_server": "http://cromwell-v51.dsde-methods.broadinstitute.org",
      "requests_timeout": 5
    }

How do these configurations affect your cromshell1.0 configs?  
Cromshell2.0 uses the same all.workflow.database.tsv as cromshell1, thus it will read-write 
to the same file. The cromshell_config.json file is new in cromshell2.0, 
changes to this file will not affect your cromshell1.0 settings.

## Development Steps

Now that you have set up your Cromshell environment, you can start adding and testing
new commands and features. There are three main steps to follow: 

1. [Add a command or feature to the codebase](../docs/addcommand.md) 
2. [Add unit and integration tests for the added scripts](../docs/addtests.md)
3. [Run test and linting scripts](../docs/runtests.md)

Once you have a functional command or feature with all of its unit/integration tests
successfully completing, then you can push your changes to the cromshell branch for review. 

## Best Practices

When styling your code use the following [site](https://peps.python.org/pep-0008/#constants)

- A well formatted function will have 
  - Lower case name with underscores as spaces
  - Parameters with the expected data structure
  - Data structure of output
  - Includes a doc string describing the function and parameters.  
```

    def alias_exists(alias_name: str, submission_file: str) -> bool:
       """
       Check if alias name already exists in submission file
       :param alias_name: Alternate string identifier for workflow submission
       :param submission_file: Path to cromshell submission file
       :return:
       """
       with open(submission_file, "r") as csv_file:
           reader = csv.DictReader(csv_file, delimiter="\t")
           for row in reader:
               if (row["ALIAS"] == alias_name) and (row["ALIAS"] != ""):
                   return True
           return False
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
