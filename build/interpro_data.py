from build.parser.interpro_data import Parser as IPDParser

from planet.models.sequences import Sequence
from planet.models.interpro import Interpro

from planet import db


def add_interpro_from_plaza(filename):
    """
    Adds GO annotation from PLAZA 3.0 to the database

    :param filename: Path to the annotation file
    :return:
    """
    interpro_parser = IPDParser()

    interpro_parser.read_plaza_interpro(filename)

    gene_hash = {}
    domain_hash = {}

    all_sequences = Sequence.query.all()
    all_domains = Interpro.query.all()

    for sequence in all_sequences:
        gene_hash[sequence.name] = sequence

    for domain in all_domains:
        domain_hash[domain.label] = domain

    for gene, domains in interpro_parser.annotation.items():
        if gene in gene_hash.keys():
            current_sequence = gene_hash[gene]
            for domain in domains:
                if domain in domain_hash.keys():
                    current_domain = domain_hash[domain]
                    if current_domain not in current_sequence.interpro_domains:
                        current_sequence.interpro_domains.append(current_domain)
                else:
                    print(domain, "not found in the database.")
        else:
            print("Gene", gene, "not found in the database.")

    try:
        db.session.commit()
    except:
        db.session.rollback()
