from build.parser.fasta import Fasta

from planet import db

from planet.models.sequences import Sequence
from planet.models.species import Species


def add_species_from_fasta(filename, species_code, species_name):
    """
    Adds a species based on a single fasta file with the coding (!) sequences

    :param filename: path to fasta file
    :param species_code: abbreviation for species (should be unique)
    :param species_name: full name of the species
    :return species_id
    """
    fasta_data = Fasta()

    fasta_data.readfile(filename)

    species = Species.query.filter_by(code=species_code).first()

    # species is not in the DB yet, add it
    if species is None:
        new_species = Species(species_code, species_name)
        db.session.add(new_species)
        db.session.commit()
        species = new_species

    new_sequences = []
    for name, sequence in fasta_data.sequences.items():
        new_sequence = {"species_id": species.id,
                        "name": name,
                        "coding_sequence": sequence,
                        "type": "protein_coding",
                        "is_mitochondrial": False,
                        "is_chloroplast": False}
        new_sequences.append(new_sequence)

        if len(new_sequences) > 400:
            new_sequences = []
            db.engine.execute(Sequence.__table__.insert(), new_sequences)
            
    db.engine.execute(Sequence.__table__.insert(), new_sequences)
    return species.id
