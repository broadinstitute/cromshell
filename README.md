```
                  __                                                            __
       .,-;-;-,. /'_\     +-----------------------------------------------+    /_'\.,-;-;-,.
     _/_/_/_|_\_\) /      |  CROMSHELL : run Cromwell jobs from the shell |     \ (/_/__|_\_\_
   '-<_><_><_><_>=/\      +-----------------------------------------------+     /\=<_><_><_><_>-'
     `/_/====/_/-'\_\                                                          /_/'-\_\====\_\'
      ""     ""    ""                                                          ""    ""     ""
```


# Installation

`cromshell` and its dependencies can be installed on OSX with `brew install broadinstitute/dsp/cromshell`

or through [bioconda](https://bioconda.github.io/) with `conda install cromshell`

Alternatively, download the script and put it somewhere...

# cromshell
 A script for submitting workflows to a cromwell server and monitoring / querying their results.

requires `column`, `curl`, `mail`, and [jq](https://stedolan.github.io/jq/)

### Examples:

```
         cromshell submit workflow.wdl inputs.json options.json dependencies.zip
         cromshell status
         cromshell -t 20 metadata
         cromshell logs -2
```

### Supported Flags:
  * `-t` `TIMEOUT`
	  * Set the curl connect timeout to `TIMEOUT` seconds.
    * Also sets the curl max timeout to `2*TIMEOUT` seconds.
    * `TIMEOUT` must be an integer.

### Supported Subcommands:

  
   ####  Start/Stop workflows
   * `submit` `[-w]` *`<wdl>`* *`<inputs_json>`* `[options_json]` `[included_wdl_zip_file]`
     * Submit a new workflow
     * *`-w`*                     Wait for workflow to transition from 'Submitted' to some other status
                                  before ${SCRIPTNAME} exits
     * *`included_wdl_zip_file`*  Zip file containing any WDL files included in the input WDL
   * `abort` *`[workflow-id] [[workflow-id]...]`*                   
     * Abort a running workflow
   #### Query workflow status:
   * `status` *`[workflow-id] [[workflow-id]...]`*                   
     * Check the status of a workflow
   * `metadata` *`[workflow-id] [[workflow-id]...]`*                
     * Get the full metadata of a workflow
   * `slim-metadata` *`[workflow-id] [[workflow-id]...]`*           
     * Get a subset of the metadata from a workflow
   * `execution-status-count` *`[-p] [-x] [workflow-id] [[workflow-id]...]`*   
     * Get the summarized status of all jobs in the workflow
     * `-p` prints a pretty summary of the execution status instead of JSON
     * `-x` expands sub-workflows for more detailed summarization
   * `timing` *`[workflow-id] [[workflow-id]...]`*                  
     * Open the timing diagram in a browser
  
   #### Logs
   * `logs` *`[workflow-id] [[workflow-id]...]`*                     
     * List the log files produced by a workflow
   * `fetch-logs` *`[workflow-id] [[workflow-id]...]`*               
     * Download all logs produced by a workflow
  
   #### Job Outputs
   * `list-outputs` *`[workflow-id] [[workflow-id]...]`*           
     *  List all output files produced by a workflow
   * `fetch-all` *`[workflow-id] [[workflow-id]...]`*             
     * Download all output files produced by a workflow
   
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
  
    
 ### Features:
 * Running `submit` will create a new folder in the `~/.cromshell/${CROMWELL_URL}/` directory named with the cromwell job id of the newly submitted job.  
 It will copy your wdl and json inputs into the folder for reproducibility.  
 * It keeps track of your most recently submitted jobs by storing their ids in `./cromshell/`  
 You may omit the job ID of the last job submitted when running commands, or use negative numbers to reference previous jobs, e.g. "-1" will track the last job, "-2" will track the one before that, and so on.
 * You can override the default cromwell server by setting the environmental variable `CROMWELL_URL` to the appropriate URL.
 * Most commands takes multiple workflow-ids, which you *can specify both in relative and absolute ID value* (i.e. `./cromwell status -1 -2 -3 c2db2989-2e09-4f2c-8a7f-c3733ae5ba7b`). 

 ### Code Conventions:
 Please try to follow these conventions when editing cromshell.
 * Use double brackets for tests ( `[[ ... ]]` instead of `[]`)
 * Use `{}` when doing dereferencing variables (`${VALUE}`,`${1}` instead of `$VALUE`,`$1`)
 * Define functions with the `function` keyword (`function doThing()` instead of `doThing()`)
