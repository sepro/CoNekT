from flask import url_for

from planet.models.relationships import SequenceFamilyAssociation

from utils.color import string_to_hex_color, string_to_shape
from utils.benchmark import benchmark

from copy import deepcopy


class CytoscapeHelper:

    @staticmethod
    @benchmark
    def parse_network(network):
        output = {"nodes": [], "edges": []}

        for n in network["nodes"]:
            output["nodes"].append({"data": n})

        for e in network["edges"]:
            output["edges"].append({"data": e})

        # add basic colors and shapes to nodes and url to gene pages

        for n in output["nodes"]:
            if n["data"]["gene_id"] is not None:
                n["data"]["gene_link"] = url_for("sequence.sequence_view", sequence_id=n["data"]["gene_id"])

            n["data"]["profile_link"] = url_for("expression_profile.expression_profile_find", probe=n["data"]["id"])
            n["data"]["color"] = "#CCC"
            n["data"]["shape"] = "ellipse"

        for e in output["edges"]:
            e["data"]["color"] = "#888"

        return output

    @staticmethod
    @benchmark
    def add_family_data_nodes(network, family_method_id):
        """
        Colors a cytoscape compatible network (dict) based on gene family

        :param network: dict containing the network
        :param family_method_id: desired type/method used to construct the families
        """
        completed_network = deepcopy(network)

        sequence_ids = []
        for node in completed_network["nodes"]:
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

        for node in completed_network["nodes"]:
            if "data" in node.keys() and "gene_id" in node["data"].keys() \
                    and node["data"]["gene_id"] in families.keys():
                node["data"]["family_color"] = string_to_hex_color(families[node["data"]["gene_id"]]["name"])
                node["data"]["family_shape"] = string_to_shape(families[node["data"]["gene_id"]]["name"])
            else:
                node["data"]["family_color"] = "#CCC"
                node["data"]["family_shape"] = "rectangle"

        return completed_network

    @staticmethod
    @benchmark
    def add_depth_data_nodes(network):
        """
        Colors a cytoscape compatible network (dict) based on edge depth
        """
        colored_network = deepcopy(network)

        colors = ["#3CE500", "#B7D800", "#CB7300", "#BF0003"]

        for node in colored_network["nodes"]:
            if "data" in node.keys() and "depth" in node["data"].keys():
                node["data"]["depth_color"] = colors[node["data"]["depth"]]

        return colored_network

    @staticmethod
    @benchmark
    def add_connection_data_nodes(network):
        colored_network = deepcopy(network)

        for node in colored_network["nodes"]:
            if "data" in node.keys() and "id" in node["data"].keys():
                probe = node["data"]["id"]
                neighbors = 0
                for edge in colored_network["edges"]:
                    if "data" in edge.keys() and "source" in edge["data"].keys() and "target" in edge["data"].keys():
                        if probe == edge["data"]["source"] or probe == edge["data"]["target"]:
                            neighbors += 1

                node["data"]["neighbors"] = neighbors

        return colored_network

    @staticmethod
    @benchmark
    def add_depth_data_edges(network):
        """
        Colors a cytoscape compatible network (dict) based on edge depth
        """
        colored_network = deepcopy(network)

        colors = ["#3CE500", "#B7D800", "#CB7300", "#BF0003"]

        for edge in colored_network["edges"]:
            if "data" in edge.keys() and "depth" in edge["data"].keys():
                edge["data"]["depth_color"] = colors[edge["data"]["depth"]]

        return colored_network
