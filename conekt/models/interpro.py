from conekt import db, whooshee
from conekt.models.relationships import sequence_interpro
from conekt.models.relationships.sequence_interpro import SequenceInterproAssociation
from conekt.models.sequences import Sequence

from utils.parser.interpro import Parser as InterproParser
from utils.parser.interpro import DomainParser as InterproDomainParser

from sqlalchemy.orm import joinedload


SQL_COLLATION = "NOCASE" if db.engine.name == "sqlite" else ""


@whooshee.register_model("description")
class Interpro(db.Model):
    __tablename__ = "interpro"
    id = db.Column(db.Integer, primary_key=True)
    label = db.Column(db.String(50, collation=SQL_COLLATION), unique=True, index=True)
    description = db.Column(db.Text)

    clade_id = db.Column(
        db.Integer, db.ForeignKey("clades.id", ondelete="SET NULL"), index=True
    )

    sequences = db.relationship("Sequence", secondary=sequence_interpro, lazy="dynamic")

    # Other properties
    # sequence_associations = defined in SequenceInterproRelationship

    def __init__(self, label, description):
        self.label = label
        self.description = description

    @property
    def species_codes(self):
        """
        Finds all species the family has genes from
        :return: a list of all species (codes)
        """

        sequences = self.sequences.options(joinedload("species")).all()

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

        sequences = self.sequences.options(joinedload("species")).all()

        output = {}

        for s in sequences:
            if s.species.code not in output:
                output[s.species.code] = 1
            else:
                output[s.species.code] += 1

        return output

    @staticmethod
    def sequence_stats(sequence_ids):
        """
        Takes a list of sequence IDs and returns InterPro stats for those sequences

        :param sequence_ids: list of sequence ids
        :return: dict with for each InterPro domain linked with any of the input sequences stats
        """
        data = SequenceInterproAssociation.query.filter(
            SequenceInterproAssociation.sequence_id.in_(sequence_ids)
        ).all()

        return Interpro.__sequence_stats_associations(data)

    @staticmethod
    def sequence_stats_subquery(sequences):
        subquery = sequences.subquery()
        data = SequenceInterproAssociation.query.join(
            subquery, SequenceInterproAssociation.sequence_id == subquery.c.id
        ).all()

        return Interpro.__sequence_stats_associations(data)

    @staticmethod
    def __sequence_stats_associations(associations):
        output = {}

        for d in associations:
            if d.interpro_id not in output.keys():
                output[d.interpro_id] = {
                    "domain": d.domain,
                    "count": 1,
                    "sequences": [d.sequence_id],
                    "species": [d.sequence.species_id],
                }
            else:
                output[d.interpro_id]["count"] += 1
                if d.sequence_id not in output[d.interpro_id]["sequences"]:
                    output[d.interpro_id]["sequences"].append(d.sequence_id)
                if d.sequence.species_id not in output[d.interpro_id]["species"]:
                    output[d.interpro_id]["species"].append(d.sequence.species_id)

        for k, v in output.items():
            v["species_count"] = len(v["species"])
            v["sequence_count"] = len(v["sequences"])

        return output

    @property
    def interpro_stats(self):
        sequence_ids = [s.id for s in self.sequences.all()]

        return Interpro.sequence_stats_subquery(self.sequences)

    @property
    def go_stats(self):
        from conekt.models.go import GO

        return GO.sequence_stats_subquery(self.sequences)

    @property
    def family_stats(self):
        from conekt.models.gene_families import GeneFamily

        return GeneFamily.sequence_stats_subquery(self.sequences)

    @staticmethod
    def add_from_xml(filename, empty=True):
        """
        Populates interpro table with domains and descriptions from the official website's XML file

        :param filename: path to XML file
        :param empty: If True the interpro table will be cleared before uploading the new domains, default = True
        """
        # If required empty the table first
        if empty:
            try:
                db.session.query(Interpro).delete()
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                print(e)

        interpro_parser = InterproParser()

        interpro_parser.readfile(filename)

        for i, domain in enumerate(interpro_parser.domains):
            interpro = Interpro(domain.label, domain.description)

            db.session.add(interpro)

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
    def add_interpro_from_plaza(filename):
        """
        Adds GO annotation from PLAZA 3.0 to the database

        :param filename: Path to the annotation file
        :return:
        """
        interpro_parser = InterproDomainParser()

        interpro_parser.read_plaza_interpro(filename)

        gene_hash = {}
        domain_hash = {}

        all_sequences = Sequence.query.all()
        all_domains = Interpro.query.all()

        for sequence in all_sequences:
            gene_hash[sequence.name] = sequence

        for domain in all_domains:
            domain_hash[domain.label] = domain

        new_domains = []

        for gene, domains in interpro_parser.annotation.items():
            if gene in gene_hash.keys():
                current_sequence = gene_hash[gene]
                for domain in domains:
                    if domain["id"] in domain_hash.keys():
                        current_domain = domain_hash[domain["id"]]

                        new_domain = {
                            "sequence_id": current_sequence.id,
                            "interpro_id": current_domain.id,
                            "start": domain["start"],
                            "stop": domain["stop"],
                        }

                        new_domains.append(new_domain)

                    else:
                        print(domain["id"], "not found in the database.")
            else:
                print("Gene", gene, "not found in the database.")

            if len(new_domains) > 400:
                db.engine.execute(
                    SequenceInterproAssociation.__table__.insert(), new_domains
                )
                new_domains = []

        db.engine.execute(SequenceInterproAssociation.__table__.insert(), new_domains)

    @staticmethod
    def add_interpro_from_interproscan(filename, species_id):
        """
        Adds GO annotation from InterProScan Output

        :param filename: Path to the annotation file
        :return:
        """
        interpro_parser = InterproDomainParser()

        interpro_parser.read_interproscan(filename)

        gene_hash = {}
        domain_hash = {}

        all_sequences = Sequence.query.filter_by(species_id=species_id)
        all_domains = Interpro.query.all()

        for sequence in all_sequences:
            gene_hash[sequence.name] = sequence

        for domain in all_domains:
            domain_hash[domain.label] = domain

        new_domains = []

        for gene, domains in interpro_parser.annotation.items():
            if gene in gene_hash.keys():
                current_sequence = gene_hash[gene]
                for domain in domains:
                    if domain["id"] in domain_hash.keys():
                        current_domain = domain_hash[domain["id"]]

                        new_domain = {
                            "sequence_id": current_sequence.id,
                            "interpro_id": current_domain.id,
                            "start": domain["start"],
                            "stop": domain["stop"],
                        }

                        new_domains.append(new_domain)

                    else:
                        print(domain["id"], "not found in the database.")
            else:
                print("Gene", gene, "not found in the database.")

            if len(new_domains) > 400:
                db.engine.execute(
                    SequenceInterproAssociation.__table__.insert(), new_domains
                )
                new_domains = []

        db.engine.execute(SequenceInterproAssociation.__table__.insert(), new_domains)
