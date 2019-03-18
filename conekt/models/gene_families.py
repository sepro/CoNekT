from conekt import db
from conekt.models.relationships import sequence_family, family_xref, family_interpro
from conekt.models.relationships.sequence_family import SequenceFamilyAssociation
from conekt.models.relationships.sequence_sequence_ecc import SequenceSequenceECCAssociation
from conekt.models.relationships.family_interpro import FamilyInterproAssociation
from conekt.models.relationships.family_go import FamilyGOAssociation
from conekt.models.sequences import Sequence
from conekt.models.interpro import Interpro
from conekt.models.go import GO

import re
import json
from collections import defaultdict, Counter

from sqlalchemy.orm import joinedload, load_only
from sqlalchemy.sql import or_, and_

SQL_COLLATION = 'NOCASE' if db.engine.name == 'sqlite' else ''


class GeneFamilyMethod(db.Model):
    __tablename__ = 'gene_family_methods'
    id = db.Column(db.Integer, primary_key=True)
    method = db.Column(db.Text)
    family_count = db.Column(db.Integer)

    families = db.relationship('GeneFamily', backref=db.backref('method', lazy='joined'),
                               lazy='dynamic',
                               cascade="all, delete-orphan",
                               passive_deletes=True)

    tree_methods = db.relationship('TreeMethod', backref=db.backref('gf_method', lazy='joined'),
                                   lazy='dynamic',
                                   cascade="all, delete-orphan",
                                   passive_deletes=True)

    def __init__(self, method):
        self.method = method

    def __str__(self):
        return "%d. %s" % (self.id, self.method)

    @staticmethod
    def drop_all_annotation():
        try:
            FamilyInterproAssociation.query.delete()
            FamilyGOAssociation.query.delete()
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(e)

    def get_interpro_annotation(self):
        families = self.families.all()

        relations = []

        for f in families:
            sequences = f.sequences.all()
            domains = []

            # Only consider families with 5 or more members
            if len(sequences) > 4:
                for s in sequences:
                    interpro_ids = list(set([i.interpro_id for i in s.interpro_associations]))

                    domains += interpro_ids

                cnt = Counter(domains)

                for interpro_id, _ in cnt.most_common(3):
                    relations.append({'gene_family_id': f.id, 'interpro_id': interpro_id})

            # add 400 sequences at the time, more can cause problems with some database engines
            if len(relations) > 400:
                db.engine.execute(FamilyInterproAssociation.__table__.insert(), relations)
                relations = []

        db.engine.execute(FamilyInterproAssociation.__table__.insert(), relations)

    def get_go_annotation(self):
        from conekt.models.relationships.sequence_go import SequenceGOAssociation
        families = self.families.all()

        relations = []

        for f in families:
            # Ignore small families
            sequence_count = len(f.sequences.all())
            if sequence_count < 5:
                break

            subquery = f.sequences.subquery()
            data = SequenceGOAssociation.query.filter(SequenceGOAssociation.predicted == 0).\
                filter(SequenceGOAssociation.evidence is not None).\
                join(subquery, SequenceGOAssociation.sequence_id == subquery.c.id).all()

            go_terms = []

            for d in data:
                if d.go.parent_count > 3:
                    go_terms.append(d.go_id)

            cnt = Counter(go_terms)
            print(f.id, cnt.most_common(5))
            for go_id, _ in cnt.most_common(5):
                print({'gene_family_id': f.id, 'go_id': go_id})
                relations.append({'gene_family_id': f.id, 'go_id': go_id})

            # add 400 sequences at the time, more can cause problems with some database engines
            if len(relations) > 400:
                db.engine.execute(FamilyGOAssociation.__table__.insert(), relations)
                relations = []

        db.engine.execute(FamilyGOAssociation.__table__.insert(), relations)

    def get_clade_distribution(self):
        """
        Will calculate the frequency of clade (per gene) for each species and return a dict of dict with counts

        counts[species_id][clade_id] = number of genes from the species associated with the Clade based on the current
        gene family method.

        :return: dict-of-dict with species_id, clade_id and then the count
        """
        counts = defaultdict(lambda: defaultdict(lambda: 0))

        for family in self.families:
            if family.clade is not None:
                for s in family.sequences:
                    counts[s.species_id][family.clade_id] += 1

        return counts

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

    @staticmethod
    def add(description):
        new_method = GeneFamilyMethod(description)

        try:
            db.session.add(new_method)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e

        return new_method


class GeneFamily(db.Model):
    __tablename__ = 'gene_families'
    id = db.Column(db.Integer, primary_key=True)
    method_id = db.Column(db.Integer, db.ForeignKey('gene_family_methods.id', ondelete='CASCADE'), index=True)
    name = db.Column(db.String(50, collation=SQL_COLLATION), unique=True, index=True)
    clade_id = db.Column(db.Integer, db.ForeignKey('clades.id', ondelete='SET NULL'), index=True)

    # Original name is used to keep track of the original ID from OrthoFinder (required to link back to trees)
    original_name = db.Column(db.String(50, collation=SQL_COLLATION), index=True, default=None)

    sequences = db.relationship('Sequence', secondary=sequence_family, lazy='dynamic')
    trees = db.relationship('Tree', backref='family', lazy='dynamic')

    interpro_domains = db.relationship('Interpro', secondary=family_interpro, lazy='dynamic')
    xrefs = db.relationship('XRef', secondary=family_xref, lazy='dynamic')

    # Other properties
    # go_annotations from .relationships.family_go FamilyGOAssociation
    # interpro_annotations from .relationships.family_intpro FamilyInterproAssociation

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

    def ecc_associations_paginated(self, page=1, page_items=30):
        sequence_ids = [s.id for s in self.sequences.all()]

        output = SequenceSequenceECCAssociation.query\
            .filter_by(gene_family_method_id=self.method_id)\
            .filter(or_(or_(*[SequenceSequenceECCAssociation.query_id == s for s in sequence_ids]),
                        or_(*[SequenceSequenceECCAssociation.target_id == s for s in sequence_ids])))\
            .paginate(page, page_items, False).items

        return output

    @staticmethod
    def sequence_stats(sequence_ids):
        """
        Takes a list of sequence IDs and returns InterPro stats for those sequences

        :param sequence_ids: list of sequence ids
        :return: dict with for each InterPro domain linked with any of the input sequences stats
        """
        data = SequenceFamilyAssociation.query.filter(SequenceFamilyAssociation.sequence_id.in_(sequence_ids)).all()

        return GeneFamily.__sequence_stats_associations(data)

    @staticmethod
    def sequence_stats_subquery(sequences):
        """
        Same as sequence_stats but takes a BaseQuery returning sequences as input (to avoid multiple times querying
        sequences by ID)

        :param sequences: BaseQuery returning sequences
        :return: dict with for each InterPro domain linked with any of the input sequences stats
        """
        subquery = sequences.subquery()

        data = SequenceFamilyAssociation.query.join(subquery, SequenceFamilyAssociation.sequence_id == subquery.c.id).all()

        return GeneFamily.__sequence_stats_associations(data)

    @staticmethod
    def __sequence_stats_associations(associations):
        output = {}
        for d in associations:
            if d.gene_family_id not in output.keys():
                output[d.gene_family_id] = {
                    'family': d.family,
                    'count': 1,
                    'sequences': [d.sequence_id],
                    'species': [d.sequence.species_id]
                }
            else:
                output[d.gene_family_id]['count'] += 1
                if d.sequence.species_id not in output[d.gene_family_id]['species']:
                    output[d.gene_family_id]['species'].append(d.sequence.species_id)

        for k, v in output.items():
            v['species_count'] = len(v['species'])

        return output

    @property
    def interpro_stats(self):
        return Interpro.sequence_stats_subquery(self.sequences)

    @property
    def go_stats(self):
        return GO.sequence_stats_subquery(self.sequences)

    @property
    def family_stats(self):
        return GeneFamily.sequence_stats_subquery(self.sequences)

    @staticmethod
    def __add_families(families, family_members):
        """
        Adds gene families to the database and assigns genes to their designated family

        :param families: list of GeneFamily objects
        :param family_members: dict (keys = gene family name) with lists of members
        """
        for i, f in enumerate(families):
            db.session.add(f)

            if i > 0 and i % 400 == 0:
                # Commit to DB every 400 records
                try:
                    db.session.commit()
                except Exception as e:
                    db.session.rollback()
                    quit()

        try:
            # Commit to DB remainder
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            quit()

        for i, f in enumerate(families):
            for member in family_members[f.name]:
                association = SequenceFamilyAssociation()

                association.sequence_id = member.id
                association.gene_family_id = f.id

                db.session.add(association)

                if i > 0 and i % 400 == 0:
                    # Commit to DB every 400 records
                    try:
                        db.session.commit()
                    except Exception as e:
                        db.session.rollback()
                        quit()

        try:
            # Commit to DB remainder
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            quit()

    @staticmethod
    def add_families_from_mcl(filename, description, handle_isoforms=False, prefix='mcl'):
        """
        Add gene families directly from MCL output (one line with all genes from one family)

        :param filename: The file to load
        :param description: Description of the method to store in the database
        :param handle_isoforms: should isoforms (indicated by .1 at the end) be handled
        :return the new methods internal ID
        """
        # Create new method for these families
        method = GeneFamilyMethod.add(description)

        gene_hash = {}
        all_sequences = Sequence.query.all()

        for sequence in all_sequences:
            gene_hash[sequence.name.lower()] = sequence

            if handle_isoforms:
                gene_id = re.sub('\.\d+$', '', sequence.name.lower())
                gene_hash[gene_id] = sequence

        families = []
        family_members = defaultdict(list)

        with open(filename, "r") as f_in:
            for i, line in enumerate(f_in, start=1):
                parts = line.strip().split()

                new_family = GeneFamily('%s_%02d_%08d' % (prefix, method.id, i))
                new_family.original_name = None
                new_family.method_id = method.id

                families.append(new_family)

                for p in parts:
                    if p.lower() in gene_hash.keys():
                        family_members[new_family.name].append(gene_hash[p.lower()])

        # add all families

        GeneFamily.__add_families(families, family_members)

        return method.id

    @staticmethod
    def add_families_from_orthofinder(filename, description, handle_isoforms=False):
        """
        Add gene families directly from OrthoFinder output (one line with all genes from one family)

        :param filename: The file to load
        :param description: Description of the method to store in the database
        :param handle_isoforms: should isoforms (indicated by .1 at the end) be handled
        :return the new methods internal ID
        """
        # Create new method for these families
        method = GeneFamilyMethod.add(description)

        gene_hash = {}
        all_sequences = Sequence.query.all()

        for sequence in all_sequences:
            gene_hash[sequence.name.lower()] = sequence

            if handle_isoforms:
                gene_id = re.sub('\.\d+$', '', sequence.name.lower())
                gene_hash[gene_id] = sequence

        families = []
        family_members = defaultdict(list)

        with open(filename, "r") as f_in:
            for line in f_in:
                orthofinder_id, *parts = line.strip().split()

                orthofinder_id = orthofinder_id.rstrip(':')

                new_family = GeneFamily(orthofinder_id.replace('OG', 'OG_%02d_' % method.id))
                new_family.original_name = orthofinder_id
                new_family.method_id = method.id

                families.append(new_family)

                for p in parts:
                    if p.lower() in gene_hash.keys():
                        family_members[new_family.name].append(gene_hash[p.lower()])

        # add all families

        GeneFamily.__add_families(families, family_members)

        return method.id

    @staticmethod
    def add_families_general(filename, description, handle_isoforms=False):
        """
        Add gene families directly from General file format output. This is the same as OrthoFinder but the identifier
        will be left alone

        :param filename: The file to load
        :param description: Description of the method to store in the database
        :param handle_isoforms: should isoforms (indicated by .1 at the end) be handled
        :return the new methods internal ID
        """
        # Create new method for these families
        method = GeneFamilyMethod.add(description)

        gene_hash = {}
        all_sequences = Sequence.query.all()

        for sequence in all_sequences:
            gene_hash[sequence.name.lower()] = sequence

            if handle_isoforms:
                gene_id = re.sub('\.\d+$', '', sequence.name.lower())
                gene_hash[gene_id] = sequence

        families = []
        family_members = defaultdict(list)

        with open(filename, "r") as f_in:
            for line in f_in:
                gf_id, *parts = line.strip().split()

                gf_id = gf_id.rstrip(':')

                new_family = GeneFamily(gf_id)
                new_family.original_name = gf_id
                new_family.method_id = method.id

                families.append(new_family)

                for p in parts:
                    if p.lower() in gene_hash.keys():
                        family_members[new_family.name].append(gene_hash[p.lower()])

        # add all families

        GeneFamily.__add_families(families, family_members)

        return method.id