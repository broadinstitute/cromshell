```
                  __                                                            __
       .,-;-;-,. /'_\     +-----------------------------------------------+    /_'\.,-;-;-,.
     _/_/_/_|_\_\) /      |  CROMSHELL : run Cromwell jobs from the shell |     \ (/_/__|_\_\_
   '-<_><_><_><_>=/\      +-----------------------------------------------+     /\=<_><_><_><_>-'
     `/_/====/_/-'\_\                                                          /_/'-\_\====\_\'
      ""     ""    ""                                                          ""    ""     ""
```

# cromshell
 A script for submitting workflows to a cromwell server and monitoring / querying their results.

requires `column`, `curl`, `mail`, and [jq](https://stedolan.github.io/jq/)

Current version: 2.0.0 

## Examples:

```
         cromshell submit workflow.wdl inputs.json options.json dependencies.zip
         cromshell status
         cromshell -t 20 metadata
         cromshell logs -2
```

## Supported Flags:
  * `-t` `TIMEOUT`
    * Set the curl connect timeout to `TIMEOUT` seconds.
    * Also sets the curl max timeout to `2*TIMEOUT` seconds.
    * `TIMEOUT` must be an integer.

## Supported Subcommands:

  
   ####  Start/Stop workflows
   * `submit` `[-w]` *`<wdl>`* *`<inputs_json>`* `[options_json]` `[included_wdl_zip_file]`
     * Submit a new workflow.
     * Will automatically validate the WDL and JSON file if `womtool` is in your path.
       * To add `womtool` to your path, install `cromwell` with brew:
         * `brew install cromwell`
     * *`-w`*                     Wait for workflow to transition from 'Submitted' to some other status
                                  before ${SCRIPTNAME} exits
     * *`included_wdl_zip_file`*  Zip file containing any WDL files included in the input WDL
   * `abort` *`[workflow-id] [[workflow-id]...]`*                   
     * Abort a running workflow.
   #### Workflow information:
   * `alias` *`<workflow-id>` `<alias_name>`* 
     * Label the given workflow ID with the given alias_name.  Aliases can be used in place of workflow IDs to reference jobs.
   #### Query workflow status:
   * `status` *`[workflow-id] [[workflow-id]...]`*                   
     * Check the status of a workflow.
   * `metadata` *`[workflow-id] [[workflow-id]...]`*                
     * Get the full metadata of a workflow.
   * `slim-metadata` *`[workflow-id] [[workflow-id]...]`*           
     * Get a subset of the metadata from a workflow.
   * `execution-status-count`, `counts` *`[-p] [-x] [workflow-id] [[workflow-id]...]`*   
     * Get the summarized status of all jobs in the workflow.
     * `-p` prints a pretty summary of the execution status instead of JSON
     * `-x` expands sub-workflows for more detailed summarization
   * `timing` *`[workflow-id] [[workflow-id]...]`*                  
     * Open the timing diagram in a browser.
  
   #### Logs
   * `logs` *`[workflow-id] [[workflow-id]...]`*                     
     * List the log files produced by a workflow.
   * `fetch-logs` *`[workflow-id] [[workflow-id]...]`*               
     * Download all logs produced by a workflow.
  
   #### Job Outputs
   * `list-outputs` *`[workflow-id] [[workflow-id]...]`*           
     *  List all output files produced by a workflow.
   * `fetch-all` *`[workflow-id] [[workflow-id]...]`*             
     * Download all output files produced by a workflow.
   
   ####  Get email notification on job completion
   * `notify` *`[workflow-id]` `[daemon-server]` `email` `[cromwell-server]`*
     * *`daemon-server`*  server to run the notification daemon on

   #### Display a list jobs submitted through cromshell
   * `list` *`[-c]` `[-u]`*                                            
     * *`-c`*    Color the output by completion status
     * *`-u`*    Check completion status of all unfinished jobs

   #### Clean up local cached list
   * `cleanup` *`[-s STATUS]`*    
     * Remove completed jobs from local list.
       Will remove all jobs from the local list that are in a completed state,
       where a completed state is one of: `Succeeded`, `Failed`, `Aborted`
     * *`-s STATUS`*     If provided, will only remove jobs with the given `STATUS` from the local list.
  
## Features:
 * Running `submit` will create a new folder in the `~/.cromshell/${CROMWELL_URL}/` directory named with the cromwell job id of the newly submitted job.  
 It will copy your wdl and json inputs into the folder for reproducibility.  
 * It keeps track of your most recently submitted jobs by storing their ids in `./cromshell/`  
 You may omit the job ID of the last job submitted when running commands, or use negative numbers to reference previous jobs, e.g. "-1" will track the last job, "-2" will track the one before that, and so on.
 * You can override the default cromwell server by setting the argument `--cromwell_url` to the appropriate URL.
 * You can override the default cromshell configuration folder by setting the environmental variable `CROMSHELL_DIR` to the appropriate directory.
 * Most commands takes multiple workflow-ids, which you *can specify both in relative and absolute ID value* (i.e. `./cromwell status -1 -2 -3 c2db2989-2e09-4f2c-8a7f-c3733ae5ba7b`). 

## Installation

    git clone git@github.com:broadinstitute/cromshell.git
    cd cromshell
    git checkout cromshell_2.0
    pip install .

    cromshell-alpha --help

## Uninstallation

    pip uninstall cromshell-alpha

## Development

To do development in this codebase, the python3 development package must
be installed.

After installation the cromshell development environment can be set up by
the following commands:

    python3 -mvenv venv
    . venv/bin/activate
    pip install -r dev-requirements.txt
    pip install -e .
    
### Running Development Builds of Cromshell

After following the above development environment setup steps, simply type
```
cromshell
```
Note that there is no leading `./` in this command.  This is due to the 
development setup adding the cromshell python script to your path.

### Linting files

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

### Tests

    # run all linting and test
    tox

    # run only (fast) unit tests
    tox -e unit

    # run only linting
    tox -e lint

### Versioning

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

