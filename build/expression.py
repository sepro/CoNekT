import json

from build.parser.planet.expression_plot import Parser as ExpressionPlotParser
from build.parser.planet.expression_network import Parser as NetworkParser
from planet import db

from planet.models.sequences import Sequence
from planet.models.species import Species
from planet.models.expression_profiles import ExpressionProfile
from planet.models.expression_networks import ExpressionNetwork, ExpressionNetworkMethod


def parse_expression_plot(plotfile, conversion):
    plot = ExpressionPlotParser()
    plot.read_plot(plotfile, conversion)

    sequences = Sequence.query.all()

    sequence_dict = {}
    for s in sequences:
        sequence_dict[s.name.upper()] = s

    for probe, profile in plot.profiles.items():

        gene_id = plot.probe_list[probe].upper()

        output = {"order": plot.conditions,
                  "data": profile}

        if gene_id in sequence_dict.keys():
            db.session.add(ExpressionProfile(probe, sequence_dict[gene_id].id, json.dumps(output)))
        else:
            db.session.add(ExpressionProfile(probe, None, json.dumps(output)))

    try:
        db.session.commit()
    except:
        db.session.rollback()


def parse_expression_network(network_file, species, description):

    # load network from hrr file
    network_parser = NetworkParser()
    network_parser.read_expression_network(network_file)

    # get all sequences from the database and create a dictionary
    sequences = Sequence.query.all()

    sequence_dict = {}
    for s in sequences:
        sequence_dict[s.name.upper()] = s

    # check if species exists

    species = Species.query.filter_by(code=species)

    if species is None:
        print("ERROR: species", species, "not found.")
        quit()

    network_method = ExpressionNetworkMethod()

    # print(json.dumps(network_parser.network["267637_at"], sort_keys=True, indent=4, separators=(',', ': ')))


