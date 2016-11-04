"""
Parser class for obo files (ontology structure files).
"""
from copy import deepcopy

import gzip


class OboEntry:
    """
    Class to store data for a single entry in an OBO file
    """
    def __init__(self):
        self.id = ''
        self.name = ''
        self.namespace = ''
        self.definition = ''
        self.is_a = []
        self.synonym = []
        self.alt_id = []
        self.extended_go = []
        self.is_obsolete = False

    def set_id(self, term_id):
        self.id = term_id

    def set_name(self, name):
        self.name = name

    def set_namespace(self, namespace):
        self.namespace = namespace

    def set_definition(self, definition):
        self.definition = definition

    def set_extended_go(self, parents):
        self.extended_go = parents

    def add_is_a(self, label):
        self.is_a.append(label)

    def add_synonym(self, label):
        self.synonym.append(label)

    def add_alt_id(self, label):
        self.alt_id.append(label)

    def make_obsolete(self):
        self.is_obsolete = True

    def process(self, key, value):
        """
        function to process new data for the current entry from the OBO file
        """
        if key == "id":
            self.set_id(value)
        elif key == "name":
            self.set_name(value)
        elif key == "namespace":
            self.set_namespace(value)
        elif key == "def":
            self.set_definition(value)
        elif key == "is_a":
            parts = value.split()
            self.add_is_a(parts[0])
        elif key == "synonym":
            self.add_synonym(value)
        elif key == "alt_id":
            self.add_alt_id(value)
        elif key == "is_obsolete" and value == "true":
            self.make_obsolete()

    def print(self):
        """
        print term to terminal
        """
        print("ID:\t\t" + self.id)
        print("Name:\t\t" + self.name)
        print("Namespace:\t" + self.namespace)
        print("Definition:\t" + self.definition)
        print("is_a: " + str(self.is_a))
        print("extended_parents: " + str(self.extended_go))

        if self.is_obsolete:
            print("OBSOLETE")


class Parser:
    """
    Reads the specified obo file
    """
    def __init__(self):
        self.terms = []

    def print(self):
        """
        prints all the terms to the terminal
        """
        for term in self.terms:
            term.print()

    def readfile(self, filename, compressed=False):
        """
        Reads an OBO file (from filename) and stores the terms as OBOEntry objects
        """
        self.terms = []

        if compressed:
            load = gzip.open
            load_type = 'rt'
        else:
            load = open
            load_type = 'r'

        with load(filename, load_type) as f:
            current_term = None

            for line in f:
                line = line.strip()
                # Skip empty
                if not line:
                    continue

                if line == "[Term]":
                    if current_term:
                        self.terms.append(current_term)
                    current_term = OboEntry()
                elif line == "[Typedef]":
                    # Skip [Typedef sections]
                    if current_term:
                        self.terms.append(current_term)
                    current_term = None
                else:
                    # Inside a [Term] environment
                    if current_term is None:
                        continue

                    key, sep, val = line.partition(":")
                    key = key.strip()
                    val = val.strip()
                    current_term.process(key, val)

            if current_term:
                self.terms.append(current_term)

    def extend_go(self):
        """
        Run this after loading the OBO file to fill the extended GO table (all parental terms of the label).
        """
        hashed_terms = {}

        for term in self.terms:
            hashed_terms[term.id] = term

        for term in self.terms:
            extended_go = deepcopy(term.is_a)

            found_new = True

            while found_new:
                found_new = False
                for parent_term in extended_go:
                    new_gos = hashed_terms[parent_term].is_a
                    for new_go in new_gos:
                        if new_go not in extended_go:
                            found_new = True
                            extended_go.append(new_go)

            term.set_extended_go(extended_go)
