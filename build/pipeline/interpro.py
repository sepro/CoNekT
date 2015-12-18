import os
import configparser

from utils.parser.fasta import Fasta
from math import ceil


def generate_script(filename, job_name, job_count, input_string, output_string, interpro_module=None, interpro_cmd="interproscan.sh", email=None):
    load_module = "" if interpro_module is None else "module load " + interpro_module
    include_email = "" if email is None else "#$ -m bea\n#$ -M " + email

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

#email
%s

#
%s
date
hostname
%s -i %s -o %s -f tsv -dp -iprlookup -goterms
date
""" % (job_name, job_count, include_email, load_module, interpro_cmd, input_string, output_string)

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

    cp = configparser.ConfigParser()
    cp.read(config)

    interpro_module = cp['GENERAL']['interpro_module']
    interpro_cmd = cp['GENERAL']['interpro_cmd']
    genomes = cp['GENERAL']['genomes'].split(';')
    email = cp['GENERAL']['email']
    jobs = cp['GENERAL']['jobs']

    for g in genomes:
        input = cp[g]['input']
        output = cp[g]['output']
        split_filenames = cp[g]['split_filenames']
        out_filenames = cp[g]['out_filenames']

        script = 'run_interpro_'+g+'.sh'
        job_name = 'interproscan_' + g

        split_fasta(input, jobs, output, filenames=split_filenames)
        generate_script(script, job_name, jobs,
                        os.path.join(output, split_filenames),
                        os.path.join(output, out_filenames),
                        interpro_module=interpro_module,
                        interpro_cmd=interpro_cmd,
                        email=email)

    print("Done !")
