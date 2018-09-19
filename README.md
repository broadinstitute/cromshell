# cromshell
shell script for interacting with cromwell servers

requires curl and [jq](https://stedolan.github.io/jq/)

### Supported Subcommands:
  * submit [wdl-file] [inputs] [options] [dependencies]
  * status [worfklow-id] [[worfklow-id]...]
  * logs [workflow-id]
  * metadata [worfklow-id]
  * execution-status-count [worfklow-id]
  * slim-metadata [worfklow-id]
  * timing [worfklow-id]
  * abort [worfklow-id]  [[worfklow-id]...]
   
 ### Features:
 * Running `submit` will create a new folder in your working directory named with the cromwell job id of the newly submitted job.  
 It will copy your wdl and json inputs into the folder for reproducibility.  
 * It keeps track of your most recently submitted jobs by storing their ids in `./cromshell/`  
 You may ommit the job ID of the last job submitted when running commands, or use negative numbers to reference previous jobs, e.g. "-1" will track the last job, "-2" will track the one before that, and so on.
 * You can override the default cromwell server by setting the environmental variable CROMWELL_URL to the appropriate URL.
 * The commands `status` and `abort` takes multiple workflow-id's, but only accepts the explicit ids when multiple ids are provided, i.e. `./cromwell status -1 -2 -3` won't work.
