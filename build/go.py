from config import DEBUG

from planet import app,db
from planet.models.go import GO
from planet.models.sequences import Sequence
from build.parser.obo import Parser as OBOParser
from build.parser.go import Parser as GOParser


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

    for gene, gos in go_parser.annotation.items():
        current_sequence = Sequence.query.filter_by(name=gene).first()
        if current_sequence is not None:
            for go in gos:
                current_go = GO.query.filter_by(label=go).first()

                if current_go is not None:
                    current_sequence.go_labels.append(current_go)
                else:
                    print("GO", go, "not found in the database.")
            try:
                db.session.commit()
            except:
                db.session.rollback()
        else:
            print("Gene", gene, "not found in the database.")


