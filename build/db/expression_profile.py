from planet import db

from planet.models.species import Species
from planet.models.sequences import Sequence
from planet.models.expression_profiles import ExpressionProfile

from collections import defaultdict
import json


def add_profile_from_lstrap(matrix_file, annotation, species_code, order=None):
    """
    Function to convert an (normalized) expression matrix (lstrap output) into a profile

    :param matrix_file: path to the annotation file
    :param annotation: dict that converts the header (htseq filename) into the condition, replicates should have the
    same name, sample to be omitted from the profile should not be included.
    :param species_code: three letter code of the species the profiles are from
    :param order: list of strings with order of conditions, None will sort alphabetically
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

        colnames = [c.replace('.htseq', '') for c in colnames]

        # determine order after annotation is not defined
        if order is None:
            order = []

            for c in colnames:
                if c in annotation.keys():
                    if annotation[c] not in order:
                        order.append(annotation[c])

            order.sort()

        # read each line and build profile
        new_probes = []
        for line in fin:
            transcript, *values = line.rstrip().split()
            profile = defaultdict(list)

            for c, v in zip(colnames, values):
                if c in annotation.keys():
                    condition = annotation[c]
                    profile[condition].append(float(v))

            sequence_id, transcript_id = transcript.split('.')

            new_probe = {"species_id": species.id,
                         "probe": transcript,
                         "sequence_id": sequence_dict[sequence_id.upper()] if sequence_id.upper() in sequence_dict.keys() else None,
                         "profile": json.dumps({"order": order, "data": profile})
                         }

            new_probes.append(new_probe)

            if len(new_probes) > 400:
                db.engine.execute(ExpressionProfile.__table__.insert(), new_probes)
                new_probes = []

        db.engine.execute(ExpressionProfile.__table__.insert(), new_probes)
