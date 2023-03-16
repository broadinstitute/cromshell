```
                  __                                                            __
       .,-;-;-,. /'_\     +-----------------------------------------------+    /_'\.,-;-;-,.
     _/_/_/_|_\_\) /      |  CROMSHELL : run Cromwell jobs from the shell |     \ (/_/__|_\_\_
   '-<_><_><_><_>=/\      +-----------------------------------------------+     /\=<_><_><_><_>-'
     `/_/====/_/-'\_\                                                          /_/'-\_\====\_\'
      ""     ""    ""                                                          ""    ""     ""
```

# cromshell
 A CLI for submitting workflows to a cromwell server and monitoring / querying their results.

Current version: 2.0.0.beta 

Cromshell 2 is the next step in the evolution Cromshell. It offers many of the same
functions as Cromshell 1 but has been rebuilt in python with many added benefits such as:
- Automatically zip dependencies when submitting a workflow.
- Added integration and unit tests to insure reliability 
- Multiple ways of installation (source, brew tap, and pypi).
- Modular architecture making adding new functionalities easier.
- Developer documentation showing how to add new features and commands to the tool.

## Examples:

```
         cromshell-beta submit workflow.wdl inputs.json options.json dependencies.zip
         cromshell-beta status
         cromshell-beta -t 20 metadata
         cromshell-beta logs -2
```

## Supported Options:
  * `--no_turtle` or `--I_hate_turtles`
    * Hide turtle logo
  * `--cromwell_url [TEXT]`
    * Specify Cromwell URL used. 
    * `TEXT` Example: `http://65.61.654.8:8000`` 
  * `-t [TIMEOUT]`
    * Specify the server connection timeout in seconds. 
    * Default is 5 sec.
    * `TIMEOUT` must be a positive integer.
  * `--gcloud_token_email [TEXT]`
    * Call `gcloud auth print-access-token` with
    this email and add the token as an auth header to requests.
  * `--referer_header_url [TEXT]`
    * For servers that require a referer, supply
    this URL in the `Referer:` header.

## Supported Subcommands:

  
   ####  Start/Stop workflows
   * `submit [-w] <wdl> <inputs_json> [options_json] [included_wdl_zip_file]`
     * Will automatically validate the WDL and JSON file.
     * Submit a new workflow.
     * *`-w`* [COMING SOON] Wait for workflow to transition from 'Submitted' to some other status before ${SCRIPTNAME} exits.
     * *`included_wdl_zip_file`*  Zip file containing any WDL files included in the input WDL
   * `abort [workflow-id] [[workflow-id]...]`               
     * Abort a running workflow.
   #### Workflow information:
   * `alias <workflow-id> <alias_name>`
     * Label the given workflow ID with the given alias_name.  Aliases can be used in place of workflow IDs to reference jobs.
     * Remove alias by passing empty double quotes as `alias_name` (e.g. `alias <workflow-id> ""`)
   #### Query workflow status:
   * `status [workflow-id] [[workflow-id]...]`                   
     * Check the status of a workflow.
   * `metadata [workflow-id] [[workflow-id]...]`                
     * Get the full metadata of a workflow.
   * `slim-metadata [workflow-id] [[workflow-id]...]`
     * Get a subset of the metadata from a workflow.
   * `counts [-j] [-x] [workflow-id] [[workflow-id]...]`   
     * Get the summarized status of all jobs in the workflow.
     * `-j` prints a JSON instead of a pretty summary of the execution status (compresses subworkflows)
     * `-x` compress sub-workflows for less detailed summarization
   * `timing` *`[workflow-id] [[workflow-id]...]`*                  

     * Open the timing diagram in a browser.
  
   #### Logs
   * `logs [workflow-id] [[workflow-id]...]`                    
     * List the log files produced by a workflow.
   * [COMING SOON] `fetch-logs [workflow-id] [[workflow-id]...]`              
     * Download all logs produced by a workflow.
  
   #### Job Outputs
   * [COMING SOON] `list-outputs [workflow-id] [[workflow-id]...]`         
     *  List all output files produced by a workflow.
   * [COMING SOON] `fetch-all [workflow-id] [[workflow-id]...]`        
     * Download all output files produced by a workflow.
   
   ####  Get email notification on job completion
   * [COMING SOON] `notify [workflow-id] [daemon-server] email [cromwell-server]`
     * *`daemon-server`*  server to run the notification daemon on

   #### Display a list jobs submitted through cromshell
   * `list [-c] [-u]`                                            
     * `-c`    Color the output by completion status
     * `-u`    Check completion status of all unfinished jobs

   #### Clean up local cached list
   * [COMING SOON] `cleanup [-s STATUS]`
     * Remove completed jobs from local list.
       Will remove all jobs from the local list that are in a completed state,
       where a completed state is one of: `Succeeded`, `Failed`, `Aborted`
     * *`-s STATUS`*     If provided, will only remove jobs with the given `STATUS` from the local list.

   #### Update cromwell server
   * `update-server`
     * Change the cromwell server that new jobs will be submitted to.
  
## Features:
 * Running `submit` will create a new folder in the `~/.cromshell/${CROMWELL_URL}/` directory named with the cromwell job id of the newly submitted job.  
 It will copy your wdl and json inputs into the folder for reproducibility.  
 * It keeps track of your most recently submitted jobs by storing their ids in `./cromshell/`  
 You may omit the job ID of the last job submitted when running commands, or use negative numbers to reference previous jobs, e.g. "-1" will track the last job, "-2" will track the one before that, and so on.
 * You can override the default cromwell server by setting the argument `--cromwell_url` to the appropriate URL.
 * You can override the default cromshell configuration folder by setting the environmental variable `CROMSHELL_CONFIG` to the appropriate directory.
 * Most commands takes multiple workflow-ids, which you *can specify both in relative and absolute ID value* (i.e. `./cromshell status -- -1 -2 -3 c2db2989-2e09-4f2c-8a7f-c3733ae5ba7b`). 
 * Assign aliases to workflow ids using the alias command (i.e. `./cromshell alias -- -1 myAliasName`).
 * Once the Alias command is used to attach an alias to a workflow id, the alias name can be used instead of the id (i.e. `./cromshell status myAliasName`).

## Installation
From brew

    brew tap broadinstitute/dsp
    brew install cromshell@2.0.0.beta.1

From pypi

    pip install -i https://test.pypi.org/simple/ cromshell-draft-release

From source

    git clone git@github.com:broadinstitute/cromshell.git
    cd cromshell
    git checkout cromshell_2.0
    pip install .

    cromshell-beta --help

## Uninstallation
From brew

    brew uninstall cromshell@2.0.0.beta.1

From pypi/source

    pip uninstall cromshell-beta

## Development

See the [Developer Docs](./developer_docs/)




