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


def parse_expression_network(network_file, species, description, score_type="rank"):
    # load network from hrr file
    network_parser = NetworkParser()
    network_parser.read_expression_network(network_file)

    # get all sequences from the database and create a dictionary
    sequences = Sequence.query.all()

    sequence_dict = {}
    for s in sequences:
        sequence_dict[s.name.upper()] = s

    # check if species exists

    species = Species.query.filter_by(code=species).first()

    if species is None:
        print("ERROR: species", species, "not found.")
        quit()

    # Add network method first
    network_method = ExpressionNetworkMethod(species.id, description, score_type)

    db.session.add(network_method)

    try:
        db.session.commit()
    except:
        db.session.rollback()

    # go over nodes, do sanity checks and add them to the db
    for node in network_parser.network.values():
        if node["gene_name"].upper() in sequence_dict.keys():
            node["gene_id"] = sequence_dict[node["gene_name"].upper()].id        # add gene_id
            node["gene_name"] = sequence_dict[node["gene_name"].upper()].name    # same case for all letters
        else:
            node["gene_id"] = None

        for linked_gene in node["linked_probes"]:
            if linked_gene["gene_name"].upper() in sequence_dict.keys():
                linked_gene["gene_id"] = sequence_dict[linked_gene["gene_name"].upper()].id
                linked_gene["gene_name"] = sequence_dict[linked_gene["gene_name"].upper()].name
            else:
                linked_gene["gene_id"] = None

        new_node = ExpressionNetwork(node["probe_name"],
                                     node["gene_id"],
                                     json.dumps(node["linked_probes"]),
                                     network_method.id)

        db.session.add(new_node)

    try:
        db.session.commit()
    except:
        db.session.rollback()

    # print(json.dumps(network_parser.network["267637_at"], sort_keys=True, indent=4, separators=(',', ': ')))
