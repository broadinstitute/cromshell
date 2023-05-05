# Legacy Cromshell 

The legacy cromshell folder contains the original cromshell script. It is no longer maintained and is only kept for historical purposes.

---

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
  
   #### Update cromwell server
   * `update-server`
     * Change the cromwell server that new jobs will be submitted to.

   #### Get cost of a workflow
   Costs are only available for workflows that completed more than 8 hours ago on a `GCS` backend.  
   Requires the `~/.cromshell/gcp_bq_cost_table.config` configuration file to exist and contain the name of the BigQuery cost table for your organization.
   Also ensure that the default project has been set using `bq init`.
   * `cost [workflow-id] [[workflow-id]...]`
     * Get the cost for a workflow.
   * `cost-detailed [workflow-id] [[workflow-id]...]`
     * Get the cost for a workflow at the task level.

    
 ### Features:
 * Running `submit` will create a new folder in the `~/.cromshell/${CROMWELL_URL}/` directory named with the cromwell job id of the newly submitted job.  
 It will copy your wdl and json inputs into the folder for reproducibility.  
 * It keeps track of your most recently submitted jobs by storing their ids in `./cromshell/`  
 You may omit the job ID of the last job submitted when running commands, or use negative numbers to reference previous jobs, e.g. "-1" will track the last job, "-2" will track the one before that, and so on.
 * You can override the default cromwell server by setting the environmental variable `CROMWELL_URL` to the appropriate URL.
 * Most commands takes multiple workflow-ids, which you *can specify both in relative and absolute ID value* (i.e. `./cromwell status -1 -2 -3 c2db2989-2e09-4f2c-8a7f-c3733ae5ba7b`). 
 * You can supply additional headers to Cromshell REST calls by setting the environmental variable `CROMSHELL_HEADER`. This is useful if your Cromwell server is fronted by an auth server that authenticates access using bearer tokens before forwarding requests onto the Cromwell API. For example: `CROMSHELL_HEADER="Authorization: Bearer 3e2f34f2e..."`

 ### Code Conventions:
 Please try to follow these conventions when editing cromshell.
 * Use double brackets for tests ( `[[ ... ]]` instead of `[]`)
 * Use `{}` when doing dereferencing variables (`${VALUE}`,`${1}` instead of `$VALUE`,`$1`)
 * Define functions with the `function` keyword (`function doThing()` instead of `doThing()`)