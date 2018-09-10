# cromshell
shell script for interacting with cromwell servers

requires curl and [jq](https://stedolan.github.io/jq/)

### Supported Subcommands:
  * submit [wdl-file] [inputs] [options] [dependencies]
  * status [worfklow-id]
  * logs [workflow-id]
  * metadata [worfklow-id]
  * execution-status-count [worfklow-id]
  * slim-metadata [worfklow-id]
  * timing [worfklow-id]
  * abort [worfklow-id]
   
 ### Features:
 * Running `submit` will create a new folder in your working directory named with the cromwell job id of the newly submitted job.  
 It will copy your wdl and json inputs into the folder for reproducibility.  
 * It keeps track of your most recently submitted jobs by storing their ids in `./cromshell/  
 You may ommit the job ID of the last job submitted when running commands, or use negative numbers to reference previous jobs.
