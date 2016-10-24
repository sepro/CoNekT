import json
import sys
import re

from utils.parser.planet.expression_plot import Parser as ExpressionPlotParser
from utils.parser.planet.expression_network import Parser as NetworkParser
from planet import db

from planet.models.sequences import Sequence
from planet.models.species import Species
from planet.models.expression_profiles import ExpressionProfile
from planet.models.expression_networks import ExpressionNetwork, ExpressionNetworkMethod


def parse_expression_plot(plotfile, conversion, species_code):

    species = Species.query.filter_by(code=species_code).first()

    # species is not in the DB yet, quit
    if species is None:
        print("Error: species not found")
        quit()

    plot = ExpressionPlotParser()
    plot.read_plot(plotfile, conversion)

    sequences = Sequence.query.filter_by(species_id=species.id).all()

    sequence_dict = {}
    for s in sequences:
        sequence_dict[s.name.upper()] = s

    new_probes = []

    for probe, profile in plot.profiles.items():
        if probe not in plot.probe_list.keys():
            print('Cannot convert', probe, '...SKIPPING!', file=sys.stderr)
            continue
        gene_id = plot.probe_list[probe].upper()

        output = {"order": plot.conditions,
                  "data": profile}

        if gene_id in sequence_dict.keys():
            new_probe = {"species_id": species.id,
                         "probe": probe,
                         "sequence_id": sequence_dict[gene_id].id,
                         "profile": json.dumps(output)}
            new_probes.append(new_probe)
        else:
            new_probe = {"species_id": species.id,
                         "probe": probe,
                         "sequence_id": None,
                         "profile": json.dumps(output)}
            new_probes.append(new_probe)

        if len(new_probes) > 400:
            db.engine.execute(ExpressionProfile.__table__.insert(), new_probes)
            new_probes = []

    db.engine.execute(ExpressionProfile.__table__.insert(), new_probes)


def parse_expression_network(network_file, species, description, score_type="rank"):
    # check if species exists

    species = Species.query.filter_by(code=species).first()

    if species is None:
        print("ERROR: species", species, "not found.")
        quit()

    # load network from hrr file
    network_parser = NetworkParser()
    network_parser.read_expression_network(network_file)

    # get all sequences for the selected organism from the database and create a dictionary
    sequences = Sequence.query.filter_by(species_id=species.id).all()

    sequence_dict = {}
    for s in sequences:
        sequence_dict[s.name.upper()] = s

    # Add network method first
    network_method = ExpressionNetworkMethod(species.id, description, score_type)

    db.session.add(network_method)

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(e)

    # go over nodes, do sanity checks and add them to the db
    new_nodes = []
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

        new_node = {"probe": node["probe_name"],
                    "sequence_id": node["gene_id"],
                    "network": json.dumps(node["linked_probes"]),
                    "method_id": network_method.id}

        new_nodes.append(new_node)

        # add nodes in sets of 400 to avoid sending to much in a single query
        if len(new_nodes) > 400:
            db.engine.execute(ExpressionNetwork.__table__.insert(), new_nodes)
            new_nodes = []

    db.engine.execute(ExpressionNetwork.__table__.insert(), new_nodes)

    return network_method.id


def read_expression_network_lstrap(network_file, species_code, description, score_type="rank", pcc_cutoff=0.7, limit=30):
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

    # Add network method first
    network_method = ExpressionNetworkMethod(species.id, description, score_type)

    db.session.add(network_method)

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(e)

    network = {}

    with open(network_file) as fin:
        for line in fin:
            query, hits = line.strip().split(' ')
            query = query.replace(':', '')

            sequence = re.sub('\.\d$', '', query)

            network[query] = {
                "probe": query,
                "sequence_id": sequence_dict[sequence.upper()] if sequence.upper() in sequence_dict.keys() else None,
                "linked_probes": [],
                "total_count": 0,
                "method_id": network_method.id
            }

            for i, h in enumerate(hits.split('\t')):
                name, value = h.split('(')
                value = float(value.replace(')', ''))
                if value > pcc_cutoff:
                    network[query]["total_count"] += 1
                    if i < limit:
                        s = re.sub('\.\d$', '', name)
                        link = {"probe_name": name,
                                "gene_name": s,
                                "gene_id": sequence_dict[s.upper()] if s.upper() in sequence_dict.keys() else None,
                                "link_score": i,
                                "link_pcc": value}
                        network[query]["linked_probes"].append(link)

            network[query]["network"] = json.dumps(network[query]["linked_probes"])

        # add nodes in sets of 400 to avoid sending to much in a single query
    new_nodes = []
    for _, n in network.items():
        new_nodes.append(n)
        if len(new_nodes) > 400:
            db.engine.execute(ExpressionNetwork.__table__.insert(), new_nodes)
            new_nodes = []

    db.engine.execute(ExpressionNetwork.__table__.insert(), new_nodes)

    return network_method.id