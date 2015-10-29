"""
Set of functions to export the database to the ftp directory
"""
import os
import gzip
import csv

from planet.models.species import Species
from planet.models.relationships import SequenceGOAssociation, SequenceFamilyAssociation, SequenceCoexpressionClusterAssociation
from planet.models.coexpression_clusters import CoexpressionCluster,CoexpressionClusteringMethod
from planet.models.gene_families import GeneFamilyMethod

from config import PLANET_FTP_DATA

SEQUENCE_PATH = os.path.join(PLANET_FTP_DATA, 'sequences')
ANNOTATION_PATH = os.path.join(PLANET_FTP_DATA, 'annotation')
FAMILIES_PATH = os.path.join(PLANET_FTP_DATA, 'families')
EXPRESSION_PATH = os.path.join(PLANET_FTP_DATA, 'expression')


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


def export_go_annotation():
    if not os.path.exists(ANNOTATION_PATH):
        os.makedirs(ANNOTATION_PATH)

    species = Species.query.all()

    for s in species:
        filename = s.code + ".go.csv.gz"
        filename = os.path.join(ANNOTATION_PATH, filename)

        sequences = s.sequences.all()

        with gzip.open(filename, 'wt') as f:
            csv_out = csv.writer(f, lineterminator='\n')
            for count, sequence in enumerate(sequences):
                # print(count, sequence.name)
                go_associations = sequence.go_associations.filter(SequenceGOAssociation.source is not None).all()
                for go_association in go_associations:
                     csv_out.writerow([sequence.name,
                                      sequence.species.code,
                                      go_association.go.label,
                                      go_association.go.name,
                                      go_association.go.type,
                                      go_association.source])


def export_interpro_annotation():
    if not os.path.exists(ANNOTATION_PATH):
        os.makedirs(ANNOTATION_PATH)

    species = Species.query.all()

    for s in species:
        filename = s.code + ".interpro.csv.gz"
        filename = os.path.join(ANNOTATION_PATH, filename)

        sequences = s.sequences.all()

        with gzip.open(filename, 'wt') as f:
            csv_out = csv.writer(f, lineterminator='\n')
            for count, sequence in enumerate(sequences):
                interpo_associations = sequence.interpro_associations.all()
                for interpro_association in interpo_associations:
                     csv_out.writerow([sequence.name,
                                      sequence.species.code,
                                      interpro_association.domain.label,
                                      interpro_association.domain.description,
                                      interpro_association.start,
                                      interpro_association.stop])


def export_families():
    if not os.path.exists(FAMILIES_PATH):
        os.makedirs(FAMILIES_PATH)

    methods = GeneFamilyMethod.query.all()

    methodsfile = os.path.join(FAMILIES_PATH, 'methods_overview.txt')

    with open(methodsfile, "w") as f:
        for m in methods:
            print(m.id, m.method, m.family_count, file=f, sep='\t')

    associations = SequenceFamilyAssociation.query.all()

    output = {}

    for a in associations:
        if a.family.method_id not in output.keys():
            output[a.family.method_id] = {}

        if a.family.name not in output[a.family.method_id].keys():
            output[a.family.method_id][a.family.name] = []

        output[a.family.method_id][a.family.name].append(a.sequence.name)

    for method, families in sorted(output.items()):
        familyfile = os.path.join(FAMILIES_PATH, 'families_method_'+str(method)+'.tab')
        with open(familyfile, "w") as f:
            for family, members in sorted(families.items()):
                print(method, family, ";".join(members), file=f, sep='\t')


def export_coexpression_clusters():
    if not os.path.exists(EXPRESSION_PATH):
        os.makedirs(EXPRESSION_PATH)

    methods = CoexpressionClusteringMethod.query.all()

    methodsfile = os.path.join(EXPRESSION_PATH, 'clustering_methods_overview.txt')

    with open(methodsfile, "w") as f:
        for m in methods:
            print(m.id, m.network_method.species.code, m.method, m.cluster_count, file=f, sep='\t')

    associations = SequenceCoexpressionClusterAssociation.query.all()

    output = {}

    for a in associations:
        if a.coexpression_cluster.method_id not in output.keys():
            output[a.coexpression_cluster.method_id] = {}

        if a.coexpression_cluster.name not in output[a.coexpression_cluster.method_id].keys():
            output[a.coexpression_cluster.method_id][a.coexpression_cluster.name] = []

        if a.sequence is not None:
            output[a.coexpression_cluster.method_id][a.coexpression_cluster.name].\
                append(a.sequence.name + "(" + a.probe + ")")
        else:
            output[a.coexpression_cluster.method_id][a.coexpression_cluster.name].\
                append("None(" + a.probe + ")")

    for method, clusters in sorted(output.items()):
        clusterfile = os.path.join(EXPRESSION_PATH, 'clustering_method_'+str(method)+'.tab')
        with open(clusterfile, "w") as f:
            for cluster, members in sorted(clusters.items()):
                print(method, cluster, ";".join(members), file=f, sep='\t')


def export_sequences():
    """
    Export all sequences (transcript and coding) to fasta files
    """
    export_coding_sequences()
    export_protein_sequences()
