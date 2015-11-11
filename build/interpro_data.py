from build.parser.plaza.interpro import Parser as IPDParser

from planet.models.sequences import Sequence
from planet.models.interpro import Interpro
from planet.models.relationships import SequenceInterproAssociation

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

    new_domains = []

    for gene, domains in interpro_parser.annotation.items():
        if gene in gene_hash.keys():
            current_sequence = gene_hash[gene]
            for domain in domains:
                if domain["id"] in domain_hash.keys():
                    current_domain = domain_hash[domain["id"]]

                    new_domain = {"sequence_id": current_sequence.id,
                                  "interpro_id": current_domain.id,
                                  "start": domain["start"],
                                  "stop": domain["stop"]}

                    new_domains.append(new_domain)

                else:
                    print(domain["id"], "not found in the database.")
        else:
            print("Gene", gene, "not found in the database.")

        if len(new_domains) > 400:
            db.engine.execute(SequenceInterproAssociation.__table__.insert(), new_domains)
            new_domains = []

    db.engine.execute(SequenceInterproAssociation.__table__.insert(), new_domains)

