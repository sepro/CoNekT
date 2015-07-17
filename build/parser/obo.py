"""
Parser class for obo files (ontology structure files).
"""
class OboEntry:
    def __init__(self):
        self.id = ''
        self.name = ''
        self.namespace = ''
        self.definition = ''
        self.is_a = []
        self.part_of = []
        self.synonym = []
        self.alt_id = []
        self.is_obsolete = False

    def set_id(self, term_id):
        self.id = term_id

    def set_name(self, name):
        self.name = name

    def set_namespace(self, namespace):
        self.namespace = namespace

    def set_definition(self, definition):
        self.definition = definition

    def add_is_a(self, label):
        self.is_a.append(label)

    def add_part_of(self, label):
        self.part_of.append(label)

    def add_synonym(self, label):
        self.synonym.append(label)

    def add_alt_id(self, label):
        self.alt_id.append(label)

    def make_obsolete(self):
        self.is_obsolete = True

    def process(self, key, value):
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

class Parser:
    """
    reads the specified obo file
    """
    def __init__(self):
        self.terms = []

    def print(self):
        for term in self.terms:
            print("ID:\t\t" + term.id)
            print("Name:\t\t" + term.name)
            print("Namespace:\t" + term.namespace)
            print("Definition:\t" + term.definition)
            print("is_a: " + str(term.is_a))
            print("part_of: " + str(term.part_of))

            if term.is_obsolete:
                print("OBSOLETE")

    def readfile(self, filename):
        """
        Reads an OBO file (from filename) and stores the terms as OBOEntry objects
        """
        self.terms = []

        with open(filename, "r") as f:
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
