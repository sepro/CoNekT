from planet import db
from planet.models.gene_families import GeneFamily
from planet.models.interpro import Interpro
from config import SQL_COLLATION

import json


class Clade(db.Model):
    __tablename__ = 'clades'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50, collation=SQL_COLLATION), unique=True, index=True)
    species = db.Column(db.Text(collation=SQL_COLLATION))
    species_count = db.Column(db.Integer)

    families = db.relationship('GeneFamily', backref='clade', lazy='dynamic')
    interpro = db.relationship('Interpro', backref='clade', lazy='dynamic')

    def __init__(self, name, species):
        self.name = name
        self.species = json.dumps(species)
        self.species_count = len(species)

    def __repr__(self):
        return str(self.id) + ". " + self.name

    @staticmethod
    def add_clade(name, species):
        """
        Add a clade to the database

        :param name: name of the clade
        :param species: list with codes (!) of the species in the clade
        """
        new_clade = Clade(name, species)
        db.session.add(new_clade)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(e)

    @staticmethod
    def update_clades():
        """
        Loop over all families and determine what clade they belong too
        """
        clades = Clade.query.all()
        families = GeneFamily.query.all()

        for f in families:
            family_species = f.species_codes

            # skip for families without members
            if len(family_species) == 0:
                f.clade_id = None
                continue

            # find the clade with the fewest species that contains all the codes
            selected_clade = None
            for c in clades:
                clade_species = json.loads(c.species)

                overlap = set(family_species).intersection(clade_species)

                if len(overlap) == len(family_species):
                    if selected_clade is None:
                        selected_clade = c
                    else:
                        if selected_clade.species_count > c.species_count:
                            selected_clade = c
            else:
                if selected_clade is None:
                    print("An error occurred, no clades found, check the clades in the database!")
                else:
                    f.clade_id = selected_clade.id

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

        for i in interpro:
            interpro_species = i.species_codes

            # skip for families without members
            if len(interpro_species) == 0:
                i.clade_id = None
                continue

            # find the clade with the fewest species that contains all the codes
            selected_clade = None
            for c in clades:
                clade_species = json.loads(c.species)

                overlap = set(interpro_species).intersection(clade_species)

                if len(overlap) == len(interpro_species):
                    if selected_clade is None:
                        selected_clade = c
                    else:
                        if selected_clade.species_count > c.species_count:
                            selected_clade = c
            else:
                if selected_clade is None:
                    print("An error occurred, no clades found, check the clades in the database!")
                else:
                    i.clade_id = selected_clade.id

        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(e)