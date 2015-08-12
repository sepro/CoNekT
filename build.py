#!/usr/bin/env python3
"""
Script to populate the database, frontend for parser functions

usage:

POPULATE DATABASE
-----------------

build.py populate_go <FILE> : populates go table with terms from an OBO file
build.py populate_interpro <FILE> : populates go table with terms from interpro.xml

ADDING SEQUENCES/SPECIES
------------------------

build.py add_fasta_species <FILE> <CODE> <NAME> : Adds the sequences (coding sequences !) to the database for the
desired species

ADDING FUNCTIONAL ANNOTATION
----------------------------

build.py add_plaza_go <FILE> : adds go annotation downloaded from PLAZA 3.0 to the database
build.py add_plaza_interpro <FILE> : adds go annotation downloaded from PLAZA 3.0 to the database

ADDING GENE FAMILIES
--------------------

build.py add_plaza_families <FILE> <DESCRIPTION>: addes gene families (from PLAZA) to the db with the
description for the method

ADDING EXPRESSION DATA
----------------------

build.py add_expression <PLOT_FILE> <CONVERSION_FILE> : adds expression plot data from PlaNet 1 pipeline to the db

"""
from flask.ext.script import Manager
from planet import app

from build.go import populate_go as pg
from build.interpro_xml import populate_interpro as pi

from build.species import add_species_from_fasta
from build.go import add_go_from_plaza
from build.interpro_data import add_interpro_from_plaza
from build.families import add_families_from_plaza

from build.expression import parse_expression_plot


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


@manager.command
def add_fasta_species(filename, species_code, species_name):
    """
    Function that adds a species based on a fasta file with coding sequences

    :param filename: path to the fasta file
    :param species_code: short code for the species (usually three letters)
    :param species_name: full name of the species
    """
    add_species_from_fasta(filename, species_code, species_name)


@manager.command
def add_plaza_go(filename):
    """
    Function that adds go information to genes from GO data downloadable from PLAZA 3.0

    :param filename: path to the data (csv file)
    """
    add_go_from_plaza(filename)


@manager.command
def add_plaza_interpro(filename):
    """
    Function that adds domain information to genes from InterPro data downloadable from PLAZA 3.0

    :param filename: path to the data (csv file)
    """
    add_interpro_from_plaza(filename)


@manager.command
def add_plaza_families(filename, description):
    """
    Function that adds gene families to genes, downloadable from PLAZA 3.0

    :param filename: path to the data (csv file)
    :param description: description of the method
    """

    add_families_from_plaza(filename, description)

@manager.command
def add_expression(plot, conversion):
    """
    Function to add expression plots (plot.txt files from PlaNet 1 pipeline). Requires a conversion table to link probes
    to sequences (e.g. .hrr file from PlaNet 1)

    :param plot: path to plot file
    :param conversion: path to conversion table
    """
    parse_expression_plot(plot, conversion)


if __name__ == "__main__":

    manager.run()

