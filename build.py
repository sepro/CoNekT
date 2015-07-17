"""
Script to populate the database, frontend for parser functions

usage:

build.py populate_go <FILE> : populates go table with terms from an OBO file

"""
from flask.ext.script import Manager
from planet import app

from build.go import populate_go as pg


manager = Manager(app)

@manager.command
def populate_go(filename):
    """
    Function that reads GO labels from an OBO file and populates the table go with this information

    :param filename: path to the OBO file
    """
    pg(filename)

if __name__ == "__main__":

    manager.run()

