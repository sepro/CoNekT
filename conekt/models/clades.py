from conekt import db
from conekt.models.species import Species
from conekt.models.gene_families import GeneFamily
from conekt.models.interpro import Interpro

from utils.phylo import get_clade

import json
import newick

SQL_COLLATION = 'NOCASE' if db.engine.name == 'sqlite' else ''


class Clade(db.Model):
    __tablename__ = 'clades'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50, collation=SQL_COLLATION), unique=True, index=True)
    species = db.Column(db.Text(collation=SQL_COLLATION))
    species_count = db.Column(db.Integer)
    newick_tree = db.Column(db.Text)

    families = db.relationship('GeneFamily', backref='clade', lazy='dynamic')
    interpro = db.relationship('Interpro', backref='clade', lazy='dynamic')

    def __init__(self, name, species, tree):
        self.name = name
        self.species = json.dumps(species)
        self.species_count = len(species)
        self.newick_tree = tree

    def __repr__(self):
        return str(self.id) + ". " + self.name

    @staticmethod
    def add_clade(name, species, tree):
        """
        Add a clade to the database

        :param name: name of the clade
        :param species: list with codes (!) of the species in the clade
        :param tree: newick tree for this clade. Will be stored in the database and used for visualizations
        """
        new_clade = Clade(name, species, tree)
        db.session.add(new_clade)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(e)

    @staticmethod
    def add_clades_from_json(data):
        """
        Adds a clade from a dict with clade details

        :param data: dict with clade details
        """
        for c, data in data.items():
            Clade.add_clade(c, data['species'], data['tree'])

    @staticmethod
    def update_clades():
        """
        Loop over all families and determine what clade they belong too. Results are stored in the database
        """
        clades = Clade.query.all()
        families = GeneFamily.query.all()

        clade_to_species = {c.name: json.loads(c.species) for c in clades}
        clade_to_id = {c.name: c.id for c in clades}

        for f in families:
            family_species = f.species_codes

            # skip for families without members
            if len(family_species) == 0:
                f.clade_id = None
                continue

            # find the clade with the fewest species that contains all the codes
            selected_clade, _  = get_clade(family_species, clade_to_species)
            if selected_clade is None:
                f.clade_id = None
            else:
                f.clade_id = clade_to_id[selected_clade]

        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(e)

    @staticmethod
    def update_clades_interpro():
        """
        Loop over all families and determine what clade they belong too
        """
        clades = Clade.query.all()
        interpro= Interpro.query.all()

        clade_to_species = {c.name: json.loads(c.species) for c in clades}
        clade_to_id = {c.name: c.id for c in clades}

        for i in interpro:
            interpro_species = i.species_codes

            # skip for families without members
            if len(interpro_species) == 0:
                i.clade_id = None
                continue

            # find the clade with the fewest species that contains all the codes
            selected_clade, _ = get_clade(interpro_species, clade_to_species)
            if selected_clade is None:
                i.clade_id = None
            else:
                i.clade_id = clade_to_id[selected_clade]

        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(e)

    @property
    def newick_tree_species(self):
        """
        Returns a Newick tree with the species present in the current clade.

        :return: Newick tree (string) with species for the current clade
        """
        species = {s.code: s.name for s in Species.query.all()}

        tree = newick.loads(self.newick_tree)[0]

        for code, name in species.items():
            node = tree.get_node(code)
            if node is not None:
                node.name = name

        return newick.dumps([tree])