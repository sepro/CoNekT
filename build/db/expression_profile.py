from planet import db

from planet.models.species import Species
from planet.models.sequences import Sequence

from collections import defaultdict
import json


def add_profile_from_lstrap(matrix_file, annotation, species_code):
    """
    Function to convert an (normalized) expression matrix (lstrap output) into a profile

    :param matrix_file: path to the annotation file
    :param annotation: dict that converts the header (htseq filename) into the condition, replicates should have the
    same name, sample to be omitted from the profile should not be included.
    :param species_code: three letter code of the species the profiles are from
    """

    # get species data, the ID is required later
    species = Species.query.filter_by(code=species_code).first()

    # species is not in the DB yet, quit
    if species is None:
        print("Error: species not found")
        quit()

    # build conversion table for sequences
    sequences = Sequence.query.filter_by(species_id=species.id).all()

    sequence_dict = {}  # key = sequence name uppercase, value internal id
    for s in sequences:
        sequence_dict[s.name.upper()] = s.id

    with open(matrix_file) as fin:
        # read header
        _, *colnames = fin.readline().rstrip().split()

        # determine order after annotation
        order = []

        for c in colnames:
            if c in annotation.keys():
                if annotation[c] not in order:
                    order.append(c)

        order.sort()

        # read each line and build profile
        for line in fin:
            transcript, *values = line.rstrip().split()
            profile = defaultdict(list)

            for c, v in zip(colnames, values):
                if c in annotation.keys():
                    condition = annotation[c]
                    profile[condition].append(float(v))

            new_probe = {"species_id": species.id,
                         "probe": transcript,
                         "sequence_id": sequence_dict[transcript.upper()] if transcript.upper() in sequence_dict.keys() else None,
                         "profile": json.dumps({"order": order, "data": profile})
                         }

            print(new_probe)
