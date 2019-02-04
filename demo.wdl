workflow Demo {

    String gatk_docker = "broadinstitute/gatk:gatkbase-2.0.2"
    call Hello {
        input:
            gatk_docker               = gatk_docker,
    }

    # ------------------------------------------------
    # Outputs:
    output {
        File summary_metrics = Hello.outFile
    }

}

task Hello {

    String gatk_docker
    String outFileName="HelloFile.txt"

    command { echo "HELLO WORLD" > ${outFileName} }

    runtime {
        cpu: 2
        memory: "4096MB"
        bootDiskSizeGb: 15
        disks: "local-disk 256 HDD"
        docker: "${gatk_docker}"
        preemptible: 0
    }

    ####################################################################################
    # Outputs:
    output { File outFile         = outFileName }
}

