from planet import db, whooshee
from planet.models.relationships import sequence_go
from planet.models.relationships.sequence_go import SequenceGOAssociation
from planet.models.sequences import Sequence

from utils.parser.obo import Parser as OBOParser
from utils.parser.plaza.go import Parser as GOParser
from utils.enrichment import hypergeo_sf, fdr_correction

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

    @property
    def short_type(self):
        if self.type == 'biological_process':
            return 'BP'
        elif self.type == 'molecular_function':
            return 'MF'
        elif self.type == 'cellular_component':
            return 'CC'
        else:
            return 'UNK'

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
    def sequence_stats(sequence_ids, exclude_predicted=True):
        """
        Takes a list of sequence IDs and returns InterPro stats for those sequences

        :param sequence_ids: list of sequence ids
        :param exclude_predicted: if True (default) predicted GO labels will be excluded
        :return: dict with for each InterPro domain linked with any of the input sequences stats
        """

        output = {}

        query = SequenceGOAssociation.query.filter(SequenceGOAssociation.sequence_id.in_(sequence_ids))

        if exclude_predicted:
            query = query.filter(SequenceGOAssociation.predicted == 0)

        data = query.all()

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

    @staticmethod
    def update_species_counts():
        """
        Adds phylo-profile to each go-label, results are stored in the database

        :param exclude_predicted: if True (default) predicted GO labels will be excluded
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
                       SequenceGOAssociation.__table__.c.go_id], distinct=True)\
            .where(SequenceGOAssociation.__table__.c.predicted == 0))\
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
        :param compressed: load data from .gz file if true (default: False)
        :param empty: Empty the database first when true (default: True)
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

    @staticmethod
    def predict_from_network(expression_network_method_id, threshold=5, source="PlaNet Prediction"):
        """
        Function to transfer GO terms from neighbors in the network. If n or more (based on threshold) neighbors have a
        GO label (excluding other predicted labels) the term is transferred.

        :param expression_network_method_id: Expression network as input
        :param threshold: number of neighboring genes that should have the label to allow transfor
        :param source: Value for the source field
        """
        from planet.models.expression.networks import ExpressionNetworkMethod

        expression_network_method = ExpressionNetworkMethod.query.get(expression_network_method_id)

        if expression_network_method is None:
            print("ERROR: Network Method ID %d not found" % expression_network_method_id)
            return

        # Get all genes that belong to the network
        probes = expression_network_method.probes.all()

        new_associations = []

        for i, probe in enumerate(probes):
            print("Predicting GO for gene: %d, %s (%d out of %d)" %
                  (probe.sequence_id, probe.sequence.name, i, expression_network_method.probe_count))

            # Get neighborhood from database
            neighborhood = json.loads(probe.network)

            # Get sequence ids from genes in first level neighborhood
            sequence_ids = [n['gene_id'] for n in neighborhood if 'gene_id' in n]

            # If the number of genes in the neighborhood is smaller than the threshold skip (no prediction possible)
            # If there is no sequence associated with the probe skip as well
            if len(sequence_ids) < threshold or probe.sequence_id is None:
                continue

            # Get own GO terms
            own_associations = SequenceGOAssociation.query.filter(SequenceGOAssociation.sequence_id == probe.sequence_id)
            own_terms = list(set([a.go_id for a in own_associations]))

            # Get GO terms from neighbors
            associations = SequenceGOAssociation.query.filter(SequenceGOAssociation.sequence_id.in_(sequence_ids)).\
                filter(SequenceGOAssociation.predicted == 0).all()

            # Make GO terms from neighbors unique and ignore terms the current gene has already
            unique_associations = set([(a.sequence_id, a.go_id) for a in associations if a.go_id not in own_terms])

            go_counts = defaultdict(lambda: 0)

            for ua in unique_associations:
                go_counts[ua[1]] += 1

            # Determine new terms (that occurred equal or more times than the desired threshold
            new_terms = [{
                'go_id': k,
                'score': v
            } for k, v in go_counts.items() if v >= threshold]

            # Store new terms in a list that can be added to the database
            for nt in new_terms:
                new_associations.append({
                    'sequence_id': probe.sequence_id,
                    'go_id': nt['go_id'],
                    'evidence': 'IEP',
                    'source': source,
                    'predicted': True,
                    'prediction_data': json.dumps({'score': nt['score'],
                                                   'threshold': threshold,
                                                   'network_method': expression_network_method_id,
                                                   'prediction_method': 'Neighbor counting'
                                                   })
                })

        # Add new labels to the database in chuncks of 400
        for i in range(0, len(new_associations), 400):
            db.engine.execute(SequenceGOAssociation.__table__.insert(), new_associations[i: i + 400])

    @staticmethod
    def predict_from_network_enrichment(expression_network_method_id, cutoff=0.05, source="PlaNet Prediction"):
        from planet.models.expression.networks import ExpressionNetworkMethod

        expression_network_method = ExpressionNetworkMethod.query.get(expression_network_method_id)

        if expression_network_method is None:
            print("ERROR: Network Method ID %d not found" % expression_network_method_id)
            return

        probes = expression_network_method.probes.all()

        # Get all GO terms and get background
        # Important, counts are obtained from precomputed counts in the species_counts field !!
        go_data = db.engine.execute(db.select([GO.__table__.c.id, GO.__table__.c.species_counts])).fetchall()

        go_background = defaultdict(lambda: 0)

        for go_id, counts_json in go_data:
            if counts_json is not "":
                counts = json.loads(counts_json)
                if str(expression_network_method.species_id) in counts.keys():
                    go_background[go_id] = counts[str(expression_network_method.species_id)]

        new_associations = []

        for i, probe in enumerate(probes):
            print("Predicting GO for gene: %d, %s (%d out of %d)" %
                  (probe.sequence_id, probe.sequence.name, i, expression_network_method.probe_count))

            # Get neighborhood from database
            neighborhood = json.loads(probe.network)

            # Get sequence ids from genes in first level neighborhood
            sequence_ids = [n['gene_id'] for n in neighborhood if 'gene_id' in n]

            # Get own GO terms
            own_associations = SequenceGOAssociation.query.filter(SequenceGOAssociation.sequence_id == probe.sequence_id)
            own_terms = list(set([a.go_id for a in own_associations]))

            # Get GO terms from neighbors
            associations = SequenceGOAssociation.query.filter(SequenceGOAssociation.sequence_id.in_(sequence_ids)).\
                filter(SequenceGOAssociation.predicted == 0).all()

            # Make GO terms from neighbors unique and ignore terms the current gene has already
            unique_associations = set([(a.sequence_id, a.go_id) for a in associations if a.go_id not in own_terms])
            go_counts = defaultdict(lambda: 0)

            for ua in unique_associations:
                go_counts[ua[1]] += 1

            # find significantly enriched GO terms and store them
            enriched_go = []

            for go_id, count in go_counts.items():
                p_value = hypergeo_sf(count, len(sequence_ids), go_background[go_id], len(probes))
                if p_value < cutoff:
                    enriched_go.append((go_id, p_value))

            # apply FDR correction to the p-values
            corrected_p = fdr_correction([a[1] for a in enriched_go])

            # push new prediction in a dict that will be added to the DB
            for corrected_p, (go_id, p_value) in zip(corrected_p, enriched_go):
                new_associations.append({
                    'sequence_id': probe.sequence_id,
                    'go_id': go_id,
                    'evidence': 'IEP',
                    'source': source,
                    'predicted': True,
                    'prediction_data': json.dumps({'p-cutoff': cutoff,
                                                   'p-value': p_value,
                                                   'p-value (FDR)': corrected_p,
                                                   'network_method': expression_network_method_id,
                                                   'prediction_method': 'Neighborhood enrichment'
                                                   })
                })

        # Add new labels to the database in chuncks of 400
        for i in range(0, len(new_associations), 400):
            db.engine.execute(SequenceGOAssociation.__table__.insert(), new_associations[i: i + 400])
