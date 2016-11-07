from planet import db
from planet.models.relationships import sequence_family, family_xref, SequenceSequenceECCAssociation
from planet.models.sequences import Sequence

from utils.parser.plaza.families import Parser as FamilyParser

import csv
import re

from sqlalchemy.orm import joinedload
from sqlalchemy.sql import or_, and_

SQL_COLLATION = 'NOCASE' if db.engine.name == 'sqlite' else ''


class GeneFamilyMethod(db.Model):
    __tablename__ = 'gene_family_methods'
    id = db.Column(db.Integer, primary_key=True)
    method = db.Column(db.Text)
    family_count = db.Column(db.Integer)

    families = db.relationship('GeneFamily', backref=db.backref('method', lazy='joined'), lazy='dynamic')

    def __init__(self, method):
        self.method = method

    @staticmethod
    def update_count():
        """
        To avoid long count queries, the number of families for a given method can be precalculated and stored in
        the database using this function.
        """
        methods = GeneFamilyMethod.query.all()

        for m in methods:
            m.family_count = m.families.count()

        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(e)


class GeneFamily(db.Model):
    __tablename__ = 'gene_families'
    id = db.Column(db.Integer, primary_key=True)
    method_id = db.Column(db.Integer, db.ForeignKey('gene_family_methods.id'), index=True)
    name = db.Column(db.String(50, collation=SQL_COLLATION), unique=True, index=True)
    clade_id = db.Column(db.Integer, db.ForeignKey('clades.id'), index=True)

    sequences = db.relationship('Sequence', secondary=sequence_family, lazy='dynamic')

    xrefs = db.relationship('XRef', secondary=family_xref, lazy='dynamic')

    def __init__(self, name):
        self.name = name

    @property
    def species_codes(self):
        """
        Finds all species the family has genes from
        :return: a list of all species (codes)
        """

        sequences = self.sequences.options(joinedload('species')).all()

        output = []

        for s in sequences:
            if s.species.code not in output:
                output.append(s.species.code)

        return output

    @property
    def species_counts(self):
        """
        Generates a phylogenetic profile of a gene family
        :return: a dict with counts per species (codes are keys)
        """

        sequences = self.sequences.options(joinedload('species')).all()

        output = {}

        for s in sequences:
            if s.species.code not in output:
                output[s.species.code] = 1
            else:
                output[s.species.code] += 1

        return output

    @property
    def ecc_associations(self):
        sequence_ids = [s.id for s in self.sequences.all()]

        output = SequenceSequenceECCAssociation.query\
            .filter_by(gene_family_method_id=self.method_id)\
            .filter(or_(or_(*[SequenceSequenceECCAssociation.query_id == s for s in sequence_ids]),
                        or_(*[SequenceSequenceECCAssociation.target_id == s for s in sequence_ids])))\
            .all()

        return output

    @staticmethod
    def add_families_from_tab(filename, description, handle_isoforms=True):

        # Create new method for these families
        method = GeneFamilyMethod(description)

        try:
            db.session.add(method)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            quit()

        gene_hash = {}
        all_sequences = Sequence.query.all()

        for sequence in all_sequences:
            gene_hash[sequence.name.lower()] = sequence

            if handle_isoforms:
                gene_id = re.sub('\.\d+$', '', sequence.name.lower())
                gene_hash[gene_id] = sequence

        family_hash = {}

        families = {}
        genes = []

        with open(filename) as csvfile:
            reader = csv.DictReader(csvfile, delimiter='\t')
            for row in reader:
                    family = row['family']
                    gene = row['gene']

                    genes.append(gene)

                    if family not in families.keys():
                        families[family] = []
                        family_hash[family] = GeneFamily(family)
                        family_hash[family].method_id = method.id

                    families[family].append(gene)

        for name, f in family_hash.items():
            db.session.add(f)

        for name, f in family_hash.items():
            for gene in families[name]:
                if gene.lower() in gene_hash.keys():
                    gene_hash[gene.lower()].families.append(family_hash[name])

        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(e)

        return method.id

    @staticmethod
    def add_families_from_plaza(filename, description):
        family_parser = FamilyParser()
        family_parser.read(filename)

        method = GeneFamilyMethod(description)

        db.session.add(method)

        gene_hash = {}
        all_sequences = Sequence.query.all()

        for sequence in all_sequences:
            gene_hash[sequence.name] = sequence

        for family, genes in family_parser.families.items():
            new_family = GeneFamily(family)
            new_family.method_id = method.id

            db.session.add(new_family)

            for gene in genes:
                if gene in gene_hash:
                    gene_hash[gene].families.append(new_family)

        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(e)

        return method.id