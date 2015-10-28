"""
Set of functions to export the database to the ftp directory
"""
import os
import gzip

from planet.models.species import Species
from config import PLANET_FTP_DATA

SEQUENCE_PATH = os.path.join(PLANET_FTP_DATA, 'sequences')


def export_coding_sequences():
    """
    Exports sequences for transcripts as gzipped fasta files to the desired path
    """
    if not os.path.exists(SEQUENCE_PATH):
        os.makedirs(SEQUENCE_PATH)

    species = Species.query.all()

    for s in species:
        filename = s.code + ".cds.fasta.gz"
        filename = os.path.join(SEQUENCE_PATH, filename)

        with gzip.open(filename, 'wb') as f:
            for sequence in s.sequences:
                f.write(bytes(">" + sequence.name + '\n' + sequence.coding_sequence + '\n', 'UTF-8'))


def export_protein_sequences():
    """
    Exports amino acid sequences for protein_coding transcripts as gzipped fasta files to the desired path
    """
    if not os.path.exists(SEQUENCE_PATH):
        os.makedirs(SEQUENCE_PATH)

    species = Species.query.all()

    for s in species:
        filename = s.code + ".aa.fasta.gz"
        filename = os.path.join(SEQUENCE_PATH, filename)

        with gzip.open(filename, 'wb') as f:
            for sequence in s.sequences:
                if sequence.type == "protein_coding":
                    f.write(bytes(">" + sequence.name + '\n' + sequence.protein_sequence + '\n', 'UTF-8'))


def export_sequences():
    """
    Export all sequences (transcript and coding) to fasta files
    """
    export_coding_sequences()
    export_protein_sequences()
