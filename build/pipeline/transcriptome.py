import configparser
import time
import subprocess

from utils.cluster import wait_for_job
from utils.cluster.templates import bowtie_build_template


class TranscriptomePipeline:
    """
    TranscriptomePipeline class. Reads a settings ini file and runs the transcriptome pipeline
    """
    def __init__(self, config):
        """
        Constructor run with path to ini file with settings

        :param config: path to setttings ini file
        """
        self.cp = configparser.ConfigParser()
        self.cp.read(config)

    def prepare_genome(self):
        """
        Runs bowtie-build for each genome on the cluster. All settings are obtained from the settings fasta file
        """
        bowtie_module = self.cp['DEFAULT']['bowtie_module']
        bowtie_build_cmd = self.cp['DEFAULT']['bowtie_build_cmd']

        genomes = self.cp['DEFAULT']['genomes'].split(';')
        email = None if self.cp['DEFAULT']['email'] == 'None' else self.cp['DEFAULT']['email']

        # Filename should include a unique timestamp !
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




