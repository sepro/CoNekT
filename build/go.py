from config import DEBUG

from planet import app,db
from planet.models.go import GO
from build.parser.obo import Parser as OBOParser


def populate_go(filename, empty=True):
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

    db.session.commit()

