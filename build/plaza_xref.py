from planet import db

from planet.models.species import Species
from planet.models.xrefs import XRef

def create_xref(species_id):
    """
    Creates xrefs to PLAZA 3.0 Dicots

    :param species: species ID of the species to process
    """
    species = Species.query.get(species_id)

    sequences = species.sequences.all()

    for s in sequences:
        xref = XRef()
        xref.name = s.name
        xref.platform = "PLAZA 3.0 Dicots"
        xref.url = "http://bioinformatics.psb.ugent.be/plaza/versions/plaza_v3_dicots/genes/view/" + s.name.upper()
        s.xrefs.append(xref)

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()

