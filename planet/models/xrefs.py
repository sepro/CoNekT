from planet import db
from planet.models.species import Species


SQL_COLLATION = 'NOCASE' if db.engine.name == 'sqlite' else ''


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
