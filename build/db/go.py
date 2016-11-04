from planet import db
from planet.models.go import GO
from planet.models.sequences import Sequence
from planet.models.relationships import SequenceGOAssociation
from utils.parser.plaza.go import Parser as GOParser

def add_go_from_plaza(filename):
    """
    Adds GO annotation from PLAZA 3.0 to the database

    :param filename: Path to the annotation file
    :return:
    """
    go_parser = GOParser()

    go_parser.read_plaza_go(filename)

    gene_hash = {}
    go_hash = {}

    all_sequences = Sequence.query.all()
    all_go = GO.query.all()

    for sequence in all_sequences:
        gene_hash[sequence.name] = sequence

    for term in all_go:
        go_hash[term.label] = term

    associations = []

    for gene, terms in go_parser.annotation.items():
        if gene in gene_hash.keys():
            current_sequence = gene_hash[gene]
            for term in terms:
                if term["id"] in go_hash.keys():
                    current_term = go_hash[term["id"]]
                    association = {
                        "sequence_id": current_sequence.id,
                        "go_id": current_term.id,
                        "evidence": term["evidence"],
                        "source": term["source"]}
                    associations.append(association)
                else:
                    print(term, "not found in the database.")
        else:
            print("Gene", gene, "not found in the database.")

        if len(associations) > 400:
            db.engine.execute(SequenceGOAssociation.__table__.insert(), associations)
            associations = []

    # Add extended GOs
    for gene, terms in go_parser.annotation.items():
        if gene in gene_hash.keys():
            current_sequence = gene_hash[gene]
            new_terms = []
            current_terms = []

            for term in terms:
                if term["id"] not in current_terms:
                    current_terms.append(term["id"])

            for term in terms:
                if term["id"] in go_hash.keys():
                    extended_terms = go_hash[term["id"]].extended_go.split(";")
                    for extended_term in extended_terms:
                        if extended_term not in current_terms and extended_term not in new_terms:
                            new_terms.append(extended_term)

            for new_term in new_terms:
                if new_term in go_hash.keys():
                    current_term = go_hash[new_term]
                    association = {
                        "sequence_id": current_sequence.id,
                        "go_id": current_term.id,
                        "evidence": None,
                        "source": "Extended"}
                    associations.append(association)

                if len(associations) > 400:
                    db.engine.execute(SequenceGOAssociation.__table__.insert(), associations)
                    associations = []

    db.engine.execute(SequenceGOAssociation.__table__.insert(), associations)
