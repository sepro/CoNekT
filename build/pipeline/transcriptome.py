import configparser
import time
import subprocess

from utils.cluster import wait_for_job


class TranscriptomePipeline:

    def __init__(self, config):
        self.cp = configparser.ConfigParser()
        self.cp.read(config)

    def prepare_genome(self):
        bowtie_module = self.cp['DEFAULT']['bowtie_module']
        bowtie_build_cmd = self.cp['DEFAULT']['bowtie_build_cmd']

        genomes = self.cp['DEFAULT']['genomes'].split(';')
        email = None if self.cp['DEFAULT']['email'] == 'None' else self.cp['DEFAULT']['email']

        load_module = "" if bowtie_module is None else "module load " + bowtie_module
        include_email = "" if email is None else "#$ -m bea\n#$ -M " + email

        filename = "bowtie_build_%d.sh" % int(time.time())

        template = """#!/bin/bash
#

#$ -N %s
#$ -cwd
#$ -j y
#$ -S /bin/bash
#$ -o OUT_$JOB_NAME.$JOB_ID
#$ -e ERR_$JOB_NAME.$JOB_ID

#email
%s

#
%s
date
hostname
%s ${in} ${out}
date
""" % ("bowtie build", include_email, load_module, bowtie_build_cmd)

        with open(filename, "w") as f:
            print(template, file=f)

        for g in genomes:
            con_file = self.cp[g]['con']
            output = self.cp[g]['con-bowtie-build']

            subprocess.run(["qsub", "-v", "in=" + con_file + ",out=" + output, filename])

        print("Preparing the genomic fasta file...")

        wait_for_job(filename)

        print("Done\n\n")

    def process_fastq(self):
        print("Processing fastq files")

        filename = ""

        wait_for_job(filename)

        print("Done\n\n")

    def run(self):
        self.prepare_genome()

        # self.process_fastq()




