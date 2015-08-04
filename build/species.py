from build.parser.fasta import Fasta

from planet import db

from planet.models.sequences import Sequence
from planet.models.species import Species


def add_species_from_fasta(filename, species_code, species_name):
    fasta_data = Fasta()

    fasta_data.readfile(filename)

    species = Species.query.filter_by(code=species_code).first()

    # species is not in the DB yet, add it
    if species is None:
        new_species = Species(species_code, species_name)
        db.session.add(new_species)
        db.session.commit()
        species = new_species

    for name, sequence in fasta_data.sequences.items():
        new_sequence = Sequence(species.id, name, sequence)
        db.session.add(new_sequence)

    db.session.commit()
