# Installation

`cromshell` and it's dependencies can be installed on OSX with `brew install broadinstitute/dsp/cromshell`

Alternatively, download the script and put it somewhere...

# cromshell
 script for interacting with cromwell servers

requires `curl`, `mail`, `column` and [jq](https://stedolan.github.io/jq/)

### Supported Subcommands:
   If no workflow-id is specified then the last submitted workflow-id is assumed.
   Alternatively, negative numbers can be used to refer to previous workflows.
     example usage:
     
     ```
         cromshell submit workflow.wdl inputs.json options.json dependencies.zip
         cromshell status
         cromshell logs -2
     ```
  
   ####  Start/Stop workflows
   * submit *wdl inputs json [options json] [included wdls]* Submit a new workflow
   * abort *[workflow-id] [[workflow-id]...]*                   Abort a running workflow
   #### Query workflow status:
   * status [workflow-id] [[workflow-id]...]                   Check the status of a workflow
   * metadata [workflow-id] [[workflow-id]...]                 Get the full metadata of a workflow
   * slim-metadata [workflow-id] [[workflow-id]...]            Get a subset of the metadata from a workflow
   * execution-status-count [workflow-id] [[workflow-id]...]   Get the summarized status of all jobs in the workflow
   * timing [workflow-id] [[workflow-id]...]                   Open the timing diagram in a browser
  
   #### Logs
   * logs [workflow-id] [[workflow-id]...]                     List the log files produced by a workflow
   * fetch-logs [workflow-id] [[workflow-id]...]               Download all logs produced by a workflow
  
   #### Job Outputs
   * list-outputs [workflow-id] [[workflow-id]...]             List all output files produced by a workflow
   * fetch-all [workflow-id] [[workflow-id]...]                Download all output files produced by a workflow
   
   *  Get email notification on job completion
      notify [workflow-id] [daemon-server] email [cromwell-server]
           daemon-server  server to run the notification daemon on

   * Display a list jobs submitted through cromshell:
      list [-c] [-u]                                            
            -c    Color the output by completion status
            -u    Check completion status of all unfinished jobs
   
 ### Features:
 * Running `submit` will create a new folder in your `~/.cromshell` directory named with the cromwell job id of the newly submitted job.  
 It will copy your wdl and json inputs into the folder for reproducibility.  
 * It keeps track of your most recently submitted jobs by storing their ids in `./cromshell/`  
 You may ommit the job ID of the last job submitted when running commands, or use negative numbers to reference previous jobs, e.g. "-1" will track the last job, "-2" will track the one before that, and so on.
 * You can override the default cromwell server by setting the environmental variable `CROMWELL_URL` to the appropriate URL.
 * Most commands takes multiple workflow-id's, but only accepts the explicit ids when multiple ids are provided, i.e. `./cromwell status -1 -2 -3` won't work.
