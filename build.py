"""
Script to populate the database, frontend for parser functions

usage:

build.py populate_go <FILE> : populates go table with terms from an OBO file
build.py populate_interpro <FILE> : populates go table with terms from interpro.xml

"""
from flask.ext.script import Manager
from planet import app

from build.go import populate_go as pg
from build.interpro_xml import populate_interpro as pi


manager = Manager(app)

@manager.command
def populate_go(filename):
    """
    Function that reads GO labels from an OBO file and populates the table go with this information

    :param filename: path to the OBO file
    """
    pg(filename)

@manager.command
def populate_interpro(filename):
    """
    Function that reads InterPro domains from official XML file and populates the table

    :param filename: path to the interpro.xml
    """
    pi(filename)

if __name__ == "__main__":

    manager.run()

