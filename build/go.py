from planet import db
from planet.models.go import GO
from planet.models.sequences import Sequence
from planet.models.relationships import SequenceGOAssociation
from build.parser.obo import Parser as OBOParser
from build.parser.plaza.go import Parser as GOParser


def populate_go(filename, empty=True):
    """
    Parses GeneOntology's OBO file and adds it to the database

    :param filename: Path to the OBO file to parse
    :param empty: Empty the database first (yes if True)
    """
    # If required empty the table first
    if empty:
        try:
            db.session.query(GO).delete()
            db.session.commit()
        except:
            db.session.rollback()

    obo_parser = OBOParser()
    obo_parser.readfile(filename)

    obo_parser.extend_go()

    for term in obo_parser.terms:
        # print(term.id + "\t" + term.name)
        go = GO(term.id, term.name, term.namespace, term.definition, term.is_obsolete, ";".join(term.is_a),
                ";".join(term.extended_go))

        db.session.add(go)

    try:
        db.session.commit()
    except:
        db.session.rollback()


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

    db.engine.execute(SequenceGOAssociation.__table__.insert(), associations)
