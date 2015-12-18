import os

from utils.parser.fasta import Fasta
from math import ceil


def generate_script(filename):

    return filename


def split_fasta(file, chunks, output_directory):
    fasta = Fasta()
    fasta.readfile(file)

    seq_per_chunk = ceil(len(fasta.sequences.keys())/chunks)

    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    for i in range(1, chunks):
        subset = fasta.remove_subset(seq_per_chunk)
        filename = "proteins_%d.fasta" % i
        filename = os.path.join(output_directory, filename)

        subset.writefile(filename)


def run_interpro(config):
    print("Running InterProScan using", config)

    print("Done !")
