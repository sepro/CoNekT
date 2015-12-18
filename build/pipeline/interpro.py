import os

from utils.parser.fasta import Fasta
from math import ceil


def generate_script(filename, job_name, job_count, input_string, output_string, interpro_module=None, interpro_cmd="interproscan.sh"):
    load_module = "" if interpro_module is None else "module load " + interpro_module

    input_string = input_string.replace('%d', "${SGE_TASK_ID}")
    output_string = output_string.replace('%d', "${SGE_TASK_ID}")

    output = """#!/bin/bash
#

#$ -q regular

#$ -N %s
#$ -cwd
#$ -j y
#$ -S /bin/bash
#$ -t 1-%d
#$ -o OUT_$JOB_NAME.$JOB_ID
#$ -e ERR_$JOB_NAME.$JOB_ID


#$ -m bea
#$ -M proost@mpimp-golm.mpg.de

#
%s
date
hostname
%s -i %s -o %s -f tsv -dp -iprlookup -goterms
date
""" % (job_name, job_count, load_module, interpro_cmd, input_string, output_string)

    with open(filename, 'w') as f:
        print(output, file=f)


def split_fasta(file, chunks, output_directory, filenames="proteins_%d.fasta"):
    fasta = Fasta()
    fasta.readfile(file)

    seq_per_chunk = ceil(len(fasta.sequences.keys())/chunks)

    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    for i in range(1, chunks+1):
        subset = fasta.remove_subset(seq_per_chunk)
        filename = filenames % i
        filename = os.path.join(output_directory, filename)

        subset.writefile(filename)


def run_interpro(config):
    print("Running InterProScan using", config)

    print("Done !")
