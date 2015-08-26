from flask import url_for
from sqlalchemy import and_

from planet.models.expression_networks import ExpressionNetwork
from planet.models.relationships import SequenceFamilyAssociation

from utils.color import string_to_hex_color
from utils.benchmark import benchmark

import json
from copy import deepcopy


class ExpressionNetworkCytoscape(ExpressionNetwork):
    """
    This class extends the ExpressionNetwork class to add specific functions to generate data compatible with
    cytoscape.js and planet_graph.js
    """
    @staticmethod
    @benchmark
    def get_neighborhood(probe, depth=0):

        network = super(ExpressionNetworkCytoscape, ExpressionNetworkCytoscape).get_neighborhood(probe, depth)

        output = {"nodes": [], "edges": []}

        for n in network["nodes"]:
            output["nodes"].append({"data": n})

        for e in network["edges"]:
            output["edges"].append({"data": e})

        # add basic colors to nodes and url to gene pages

        for n in output["nodes"]:
            if n["data"]["gene_id"] is not None:
                n["data"]["gene_link"] = url_for("sequence.sequence_view", sequence_id=n["data"]["gene_id"])
            n["data"]["color"] = "#CCC"

        for e in output["edges"]:
            e["data"]["color"] = "#888"

        return output

    @staticmethod
    @benchmark
    def colorize_network_family(network, family_method_id):
        """
        Colors a cytoscape compatible network (dict) based on gene family

        :param network: dict containing the network
        :param family_method_id: desired type/method used to construct the families
        """
        colored_network = deepcopy(network)

        sequence_ids = []
        for node in colored_network["nodes"]:
            if "data" in node.keys() and "gene_id" in node["data"].keys():
                sequence_ids.append(node["data"]["gene_id"])

        sequence_families = SequenceFamilyAssociation.query.\
            filter(SequenceFamilyAssociation.sequence_id.in_(sequence_ids)).all()

        families = {}

        for s in sequence_families:
            if s.family.method_id == family_method_id:
                families[s.sequence_id] = {}
                families[s.sequence_id]["name"] = s.family.name
                families[s.sequence_id]["id"] = s.gene_family_id

        for node in colored_network["nodes"]:
            if "data" in node.keys() and "gene_id" in node["data"].keys() \
                    and node["data"]["gene_id"] in families.keys():
                node["data"]["color"] = string_to_hex_color(families[node["data"]["gene_id"]]["name"])

        return colored_network
