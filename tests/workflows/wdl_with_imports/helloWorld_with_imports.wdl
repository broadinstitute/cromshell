import "../helloWorld.wdl" as HelloWorldWorkflow
import "hello_world_task.wdl" as helloWorldTask

workflow HelloWorld {
    meta {
        workflow_description: "echos hello world"
    }
    parameter_meta {
        # Description of inputs:
        #   Required:
        docker: "Docker image in which to run"
        #   Optional:
        mem: "Amount of memory to give to the machine running each task in this workflow."
        preemptible_attempts: "Number of times to allow each task in this workflow to be preempted."
        disk_space_gb: "Amount of storage disk space (in Gb) to give to each machine running each task in this workflow."
        cpu: "Number of CPU cores to give to each machine running each task in this workflow."
        boot_disk_size_gb: "Amount of boot disk space (in Gb) to give to each machine running each task in this workflow."
    }
    String docker

    Int? mem
    Int? preemptible_attempts
    Int? disk_space_gb
    Int? cpu
    Int? boot_disk_size_gb

        call helloWorldTask.HelloWorldTask {
            input:
                docker               = docker,
                mem                  = mem,
                preemptible_attempts = preemptible_attempts,
                disk_space_gb        = disk_space_gb,
                cpu                  = cpu,
                boot_disk_size_gb    = boot_disk_size_gb
        }

    output {
        File output_file = HelloWorldTask.output_file
    }
}


