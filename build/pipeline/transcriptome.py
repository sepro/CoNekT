import configparser
import time
import subprocess

from utils.cluster import wait_for_job
from utils.cluster.templates import bowtie_build_template


class TranscriptomePipeline:

    def __init__(self, config):
        self.cp = configparser.ConfigParser()
        self.cp.read(config)

    def prepare_genome(self):
        bowtie_module = self.cp['DEFAULT']['bowtie_module']
        bowtie_build_cmd = self.cp['DEFAULT']['bowtie_build_cmd']

        genomes = self.cp['DEFAULT']['genomes'].split(';')
        email = None if self.cp['DEFAULT']['email'] == 'None' else self.cp['DEFAULT']['email']

        filename = "bowtie_build_%d.sh" % int(time.time())

        template = bowtie_build_template("bowtie build", email, bowtie_module, bowtie_build_cmd)

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




