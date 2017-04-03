from planet import db, whooshee
from planet.models.relationships import sequence_go
from planet.models.relationships.sequence_go import SequenceGOAssociation
from planet.models.sequences import Sequence

from utils.parser.obo import Parser as OBOParser
from utils.parser.plaza.go import Parser as GOParser

from collections import defaultdict

import json

SQL_COLLATION = 'NOCASE' if db.engine.name == 'sqlite' else ''


@whooshee.register_model('name', 'description')
class GO(db.Model):
    __tablename__ = 'go'
    id = db.Column(db.Integer, primary_key=True)
    label = db.Column(db.String(50, collation=SQL_COLLATION), unique=True, index=True)
    name = db.Column(db.Text)
    type = db.Column(db.Enum('biological_process', 'molecular_function', 'cellular_component', name='go_type'))
    description = db.Column(db.Text)
    obsolete = db.Column(db.Boolean)
    is_a = db.Column(db.Text)
    extended_go = db.Column(db.Text)
    species_counts = db.Column(db.Text)

    sequences = db.relationship('Sequence', secondary=sequence_go, lazy='dynamic')

    # Other properties
    #
    # sequence_associations declared in 'SequenceGOAssociation'
    # enriched_clusters declared in 'ClusterGOEnrichment'

    def __init__(self, label, name, go_type, description, obsolete, is_a, extended_go):
        self.label = label
        self.name = name
        self.type = go_type
        self.description = description
        self.obsolete = obsolete
        self.is_a = is_a
        self.extended_go = extended_go
        self.species_counts = ""

    def set_all(self, label, name, go_type, description, extended_go):
        self.label = label
        self.name = name
        self.type = go_type
        self.description = description
        self.extended_go = extended_go
        self.species_counts = ""

    def species_occurrence(self, species_id):
        """
        count how many genes have the current GO term in a given species

        :param species_id: internal id of the selected species
        :return: count of sequences with this term associated
        """
        count = 0
        sequences = self.sequences.all()

        for s in sequences:
            if s.species_id == species_id:
                count += 1

        return count

    @staticmethod
    def sequence_stats(sequence_ids):
        """
        Takes a list of sequence IDs and returns InterPro stats for those sequences

        :param sequence_ids: list of sequence ids
        :return: dict with for each InterPro domain linked with any of the input sequences stats
        """

        output = {}

        data = SequenceGOAssociation.query.filter(SequenceGOAssociation.sequence_id.in_(sequence_ids)).all()

        for d in data:
            if d.go_id not in output.keys():
                output[d.go_id] = {
                    'go': d.go,
                    'count': 1,
                    'sequences': [d.sequence_id],
                    'species': [d.sequence.species_id]
                }
            else:
                output[d.go_id]['count'] += 1
                if d.sequence_id not in output[d.go_id]['sequences']:
                    output[d.go_id]['sequences'].append(d.sequence_id)
                if d.sequence.species_id not in output[d.go_id]['species']:
                    output[d.go_id]['species'].append(d.sequence.species_id)

        for k, v in output.items():
            v['species_count'] = len(v['species'])
            v['sequence_count'] = len(v['sequences'])

        return output

    @property
    def interpro_stats(self):
        from planet.models.interpro import Interpro
        sequence_ids = [s.id for s in self.sequences.all()]

        return Interpro.sequence_stats(sequence_ids)

    @property
    def go_stats(self):
        sequence_ids = [s.id for s in self.sequences.all()]

        return GO.sequence_stats(sequence_ids)

    @property
    def family_stats(self):
        from planet.models.gene_families import GeneFamily
        sequence_ids = [s.id for s in self.sequences.all()]

        return GeneFamily.sequence_stats(sequence_ids)

    @staticmethod
    def update_species_counts():
        """
        adds phylo-profile to each go-label, results are stored in the database
        """
        # link species to sequences
        sequences = db.engine.execute(db.select([Sequence.__table__.c.id, Sequence.__table__.c.species_id])).fetchall()

        sequence_to_species = {}
        for seq_id, species_id in sequences:
            if species_id is not None:
                sequence_to_species[seq_id] = int(species_id)

        # get go for all genes
        associations = db.engine.execute(
            db.select([SequenceGOAssociation.__table__.c.sequence_id,
                       SequenceGOAssociation.__table__.c.go_id], distinct=True))\
            .fetchall()

        count = {}
        for seq_id, go_id in associations:
            species_id = sequence_to_species[seq_id]

            if go_id not in count.keys():
                count[go_id] = {}

            if species_id not in count[go_id]:
                count[go_id][species_id] = 1
            else:
                count[go_id][species_id] += 1

        # update counts
        for go_id, data in count.items():
            db.engine.execute(db.update(GO.__table__)
                              .where(GO.__table__.c.id == go_id)
                              .values(species_counts=json.dumps(data)))

    @staticmethod
    def add_from_obo(filename, empty=True, compressed=False):
        """
        Parses GeneOntology's OBO file and adds it to the database

        :param filename: Path to the OBO file to parse
        :param empty: Empty the database first (yes if True)
        """
        # If required empty the table first
        if empty:
            try:
                db.session.query(GO).delete()
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                print(e)

        obo_parser = OBOParser()
        obo_parser.readfile(filename, compressed=compressed)

        obo_parser.extend_go()

        for i, term in enumerate(obo_parser.terms):
            go = GO(term.id, term.name, term.namespace, term.definition, term.is_obsolete, ";".join(term.is_a),
                    ";".join(term.extended_go))

            db.session.add(go)

            if i % 40 == 0:
                # commit to the db frequently to allow WHOOSHEE's indexing function to work without timing out
                try:
                    db.session.commit()
                except Exception as e:
                    db.session.rollback()
                    print(e)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(e)

    @staticmethod
    def add_go_from_plaza(filename):
        """
        Adds GO annotation from PLAZA 3.0 to the database

        :param filename: Path to the annotation file
        :return:
        """
        go_parser = GOParser()

        go_parser.read_plaza_go(filename)

        gene_hash = {}
        go_hash = {}

        all_sequences = Sequence.query.all()
        all_go = GO.query.all()

        for sequence in all_sequences:
            gene_hash[sequence.name] = sequence

        for term in all_go:
            go_hash[term.label] = term

        associations = []

        for gene, terms in go_parser.annotation.items():
            if gene in gene_hash.keys():
                current_sequence = gene_hash[gene]
                for term in terms:
                    if term["id"] in go_hash.keys():
                        current_term = go_hash[term["id"]]
                        association = {
                            "sequence_id": current_sequence.id,
                            "go_id": current_term.id,
                            "evidence": term["evidence"],
                            "source": term["source"]}
                        associations.append(association)
                    else:
                        print(term, "not found in the database.")
            else:
                print("Gene", gene, "not found in the database.")

            if len(associations) > 400:
                db.engine.execute(SequenceGOAssociation.__table__.insert(), associations)
                associations = []

        # Add extended GOs
        for gene, terms in go_parser.annotation.items():
            if gene in gene_hash.keys():
                current_sequence = gene_hash[gene]
                new_terms = []
                current_terms = []

                for term in terms:
                    if term["id"] not in current_terms:
                        current_terms.append(term["id"])

                for term in terms:
                    if term["id"] in go_hash.keys():
                        extended_terms = go_hash[term["id"]].extended_go.split(";")
                        for extended_term in extended_terms:
                            if extended_term not in current_terms and extended_term not in new_terms:
                                new_terms.append(extended_term)

                for new_term in new_terms:
                    if new_term in go_hash.keys():
                        current_term = go_hash[new_term]
                        association = {
                            "sequence_id": current_sequence.id,
                            "go_id": current_term.id,
                            "evidence": None,
                            "source": "Extended"}
                        associations.append(association)

                    if len(associations) > 400:
                        db.engine.execute(SequenceGOAssociation.__table__.insert(), associations)
                        associations = []

        db.engine.execute(SequenceGOAssociation.__table__.insert(), associations)

    @staticmethod
    def add_go_from_tab(filename, species_id, source="Source not provided"):
        gene_hash = {}
        go_hash = {}

        all_sequences = Sequence.query.filter_by(species_id=species_id).all()
        all_go = GO.query.all()

        for sequence in all_sequences:
            gene_hash[sequence.name] = sequence

        for term in all_go:
            go_hash[term.label] = term

        associations = []

        gene_go = defaultdict(list)

        with open(filename, "r") as f:
            for line in f:
                gene, term, evidence = line.strip().split('\t')
                if gene in gene_hash.keys():
                    current_sequence = gene_hash[gene]
                    if term in go_hash.keys():
                        current_term = go_hash[term]
                        association = {
                            "sequence_id": current_sequence.id,
                            "go_id": current_term.id,
                            "evidence": evidence,
                            "source": source}
                        associations.append(association)

                        if term not in gene_go[gene]:
                            gene_go[gene].append(term)

                    else:
                        print(term, "not found in the database.")
                else:
                    print("Gene", gene, "not found in the database.")

                if len(associations) > 400:
                    db.engine.execute(SequenceGOAssociation.__table__.insert(), associations)
                    associations = []

        # Add extended GOs
        for gene, terms in gene_go.items():
            if gene in gene_hash.keys():
                current_sequence = gene_hash[gene]
                new_terms = []
                current_terms = []

                for term in terms:
                    if term not in current_terms:
                        current_terms.append(term)

                for term in terms:
                    if term in go_hash.keys():
                        extended_terms = go_hash[term].extended_go.split(";")
                        for extended_term in extended_terms:
                            if extended_term not in current_terms and extended_term not in new_terms:
                                new_terms.append(extended_term)

                for new_term in new_terms:
                    if new_term in go_hash.keys():
                        current_term = go_hash[new_term]
                        association = {
                            "sequence_id": current_sequence.id,
                            "go_id": current_term.id,
                            "evidence": None,
                            "source": "Extended"}
                        associations.append(association)

                    if len(associations) > 400:
                        db.engine.execute(SequenceGOAssociation.__table__.insert(), associations)
                        associations = []

        db.engine.execute(SequenceGOAssociation.__table__.insert(), associations)