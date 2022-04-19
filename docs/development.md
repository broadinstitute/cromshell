# Development

Welcome to Cromshells development document, here you will find instructions 
on setting up environment to develop, adding new commands, testing, and other
relevant material. 

## Getting Started
To do development in this codebase, the python3 development package must
be installed.

After installation the cromshell development environment can be set up by
the following commands:

1. Install from source


    git clone git@github.com:broadinstitute/cromshell.git
    cd cromshell
    git checkout cromshell_2.0

2. Create python environment


    python3 -mvenv venv
    . venv/bin/activate
    pip install -r dev-requirements.txt
    pip install -e .


    
### Running Development Builds of Cromshell

After following the above development environment setup steps, cromshell should 
have been added to your path.
Run `cromshell-alpha --help` to confirm installation.

    > cromshell-alpha --help
    Usage: cromshell-alpha [OPTIONS] COMMAND [ARGS]...
    
      Cromshell is a script for submitting workflows to a cromwell server and
      monitoring / querying their results.
    


Note that there is no leading `./` in this command.  This is due to the 
development setup adding the cromshell python script to your path.

### Setup Cromshell configuration files

Cromshell will automatically create a hidden directory containing configuration files after running a command if they don’t already exist. 

Run
```cromshell-alpha version```

The following directory and files should be created

    > ~./cromshell
            all.workflow.database.tsv
            cromshell_config.json


All.workflow.database.tsv : Tab-delimited file listing all workflows executed by the user
Cromshell_config.json : Configuration file for cromshell
Edit the cromshe_config file so that the proper Cromwell server is being used, for example

    {
      "cromwell_server": "http://cromwell-v51.dsde-methods.broadinstitute.org",
      "requests_timeout": 5
    }

How do these configurations affect your cromshell1.0 configs? 
Cromshell2.0 uses the same all.workflow.database.tsv as cromshell1 so will read-write to the same file. The cromshell_config.json file is new in cromshell2.0, changes to this file will not affect your cromshell1.0 settings.

## Steps to contributing to Cromshell

1. [Add command](../docs/addcommand.md) 
2. [Add unit and integration tests](../docs/addtests.md)
3. [Running tests and linting](../docs/runtests.md)

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

## Best Practices

When styling your code use the following [site](https://peps.python.org/pep-0008/#constants)

A well formatted function will have 
- Lower case name with underscores as spaces
- Parameters with the expected data structure
- Data structure of output
- Includes a doc string describing the function and parameters


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











