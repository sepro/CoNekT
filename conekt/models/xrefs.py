from conekt import db, whooshee
from conekt.models.species import Species
from conekt.models.gene_families import GeneFamilyMethod


SQL_COLLATION = 'NOCASE' if db.engine.name == 'sqlite' else ''


@whooshee.register_model('name')
class XRef(db.Model):
    __tablename__ = 'xrefs'
    id = db.Column(db.Integer, primary_key=True)
    platform = db.Column(db.String(50, collation=SQL_COLLATION), index=True)
    name = db.Column(db.String(50, collation=SQL_COLLATION), index=True)
    url = db.Column(db.Text())

    @staticmethod
    def __create_xref_genes(species_id, platform, url):
        """
        Creates xrefs to PLAZA 3.0 Dicots

        :param species_id: species ID of the species to process
        """
        species = Species.query.get(species_id)

        sequences = species.sequences.all()

        for s in sequences:
            xref = XRef()
            xref.name = s.name
            xref.platform = platform
            xref.url = url % s.name.upper()
            s.xrefs.append(xref)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()

    @staticmethod
    def create_plaza_xref_genes(species_id):
        """
        Creates xrefs to PLAZA 3.0 Dicots

        :param species_id: species ID of the species to process
        """
        XRef.__create_xref_genes(species_id, "PLAZA 3.0 Dicots", "http://bioinformatics.psb.ugent.be/plaza/versions/plaza_v3_dicots/genes/view/%s")

    @staticmethod
    def create_evex_xref_genes(species_id):
        """
        Creates xrefs to EVEX

        :param species_id: species ID of the species to process
        """
        XRef.__create_xref_genes(species_id, "EVEX", "http://www.evexdb.org/search/?search=%s")

    @staticmethod
    def add_xref_genes_from_file(species_id, filename):
        species = Species.query.get(species_id)

        sequences = species.sequences.all()
        seq_dict = {s.name.upper(): s for s in sequences}

        with open(filename, "r") as f:
            for i, line in enumerate(f):
                sequence, name, platform, url = line.split('\t')

                xref = XRef()
                xref.name = name
                xref.platform = platform
                xref.url = url

                if sequence.upper() in seq_dict.keys():
                    s = seq_dict[sequence.upper()]
                    s.xrefs.append(xref)

                if i % 400 == 0:
                    # Update every 400 lines
                    try:
                        db.session.commit()
                    except Exception as e:
                        db.session.rollback()

            # Commit final changes
            try:
                db.session.commit()
            except Exception as e:
                db.session.rollback()

    @staticmethod
    def add_xref_families_from_file(gene_family_method_id, filename):
        gf_method = GeneFamilyMethod.query.get(gene_family_method_id)

        families = gf_method.families.all()

        fam_dict = {f.name.upper(): f for f in families}

        with open(filename, "r") as f:
            for line in f:
                family, name, platform, url = line.split('\t')

                xref = XRef()
                xref.name = name
                xref.platform = platform
                xref.url = url

                if family.upper() in fam_dict.keys():
                    f = fam_dict[family.upper()]
                    f.xrefs.append(xref)
                    try:
                        db.session.commit()
                    except Exception as e:
                        db.session.rollback()
