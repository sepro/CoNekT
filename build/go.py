from config import DEBUG

from planet import app,db
from planet.models.go import GO
from build.parser.obo import Parser as OBOParser


def populate_go(filename):
    obo_parser = OBOParser()
    obo_parser.readfile(filename)

    for term in obo_parser.terms:
        # print(term.id + "\t" + term.name)
        go = GO(term.id, term.name, term.namespace, term.definition, "")

        db.session.add(go)

    db.session.commit()

