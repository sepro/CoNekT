from utils.parser.fasta import Fasta

from planet import db

from planet.models.sequences import Sequence
from planet.models.species import Species


def add_species_from_fasta(filename, species_code, species_name, contains_description=False,
                           is_mitochondrial=False,
                           is_chloroplast=False):
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
        description = ''
        if contains_description:
            parts = name.split('|', 1)
            name = parts[0].strip()
            description = parts[1].strip()

        new_sequence = {"species_id": species.id,
                        "name": name,
                        "description": description,
                        "coding_sequence": sequence,
                        "type": "protein_coding",
                        "is_mitochondrial": is_mitochondrial,
                        "is_chloroplast": is_chloroplast}
        new_sequences.append(new_sequence)

        # add 400 sequences at the time, more can cause problems with some database engines
        if len(new_sequences) > 400:
            db.engine.execute(Sequence.__table__.insert(), new_sequences)
            new_sequences = []

    # add the last set of sequences
    db.engine.execute(Sequence.__table__.insert(), new_sequences)

    return species.id
