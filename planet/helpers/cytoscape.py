from flask import url_for
from sqlalchemy.orm import joinedload

from planet.models.relationships import SequenceFamilyAssociation, SequenceInterproAssociation
from planet.models.sequences import Sequence

from utils.color import family_to_shape_and_color
from copy import deepcopy


class CytoscapeHelper:

    @staticmethod
    def parse_network(network):
        """
        Parses a network generated by the ExpressionNetwork and CoexpressionCluster model, adding basic information
        and exporting the whole thing to a cytoscape.js compatible

        :param network: internal id of the network
        :return: Network fully compatible with Cytoscape.js
        """
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
    def add_family_data_nodes(network, family_method_id):
        """
        Adds family, clade and interpro information to a a cytoscape compatible network (dict)

        :param network: dict containing the network
        :param family_method_id: desired type/method used to construct the families

        :return: Cytoscape.js compatible network with family, clade and interpro information included
        """
        completed_network = deepcopy(network)

        sequence_ids = []
        for node in completed_network["nodes"]:
            if "data" in node.keys() and "gene_id" in node["data"].keys():
                sequence_ids.append(node["data"]["gene_id"])

        sequence_families = SequenceFamilyAssociation.query.\
            filter(SequenceFamilyAssociation.sequence_id.in_(sequence_ids)).\
            options(joinedload('family.clade')).\
            filter(SequenceFamilyAssociation.family.has(method_id=family_method_id)).all()

        sequence_interpro = SequenceInterproAssociation.query.\
            filter(SequenceInterproAssociation.sequence_id.in_(sequence_ids)).all()

        data = {}

        for s in sequence_families:
            data[s.sequence_id] = {}
            data[s.sequence_id]["name"] = s.family.name
            data[s.sequence_id]["id"] = s.gene_family_id
            data[s.sequence_id]["url"] = url_for('family.family_view', family_id=s.gene_family_id)
            if s.family.clade is not None:
                data[s.sequence_id]["clade"] = s.family.clade.name
                data[s.sequence_id]["clade_count"] = s.family.clade.species_count
            else:
                data[s.sequence_id]["clade"] = "None"
                data[s.sequence_id]["clade_count"] = 0

        for i in sequence_interpro:
            if "interpro" in data[i.sequence_id]:
                data[i.sequence_id]["interpro"] += [i.domain.label]
            else:
                data[i.sequence_id]["interpro"] = [i.domain.label]

        for node in completed_network["nodes"]:
            if "data" in node.keys() and "gene_id" in node["data"].keys() \
                    and node["data"]["gene_id"] in data.keys():
                if "interpro" in data[node["data"]["gene_id"]]:
                    node["data"]["interpro"] = data[node["data"]["gene_id"]]["interpro"]
                node["data"]["family_name"] = data[node["data"]["gene_id"]]["name"]
                node["data"]["family_id"] = data[node["data"]["gene_id"]]["id"]
                node["data"]["family_clade"] = data[node["data"]["gene_id"]]["clade"]
                node["data"]["family_clade_count"] = data[node["data"]["gene_id"]]["clade_count"]
            else:
                node["data"]["family_name"] = None
                node["data"]["family_id"] = None
                node["data"]["family_url"] = None
                node["data"]["family_color"] = "#CCC"
                node["data"]["family_shape"] = "rectangle"
                node["data"]["family_clade"] = "None"
                node["data"]["family_clade_count"] = 1

        return completed_network

    @staticmethod
    def add_lc_data_nodes(network):
        """
        Colors a network based on family information and label co-occurrences.

        :param network: dict containing the network
        :return: Cytoscape.js compatible network with colors and shapes based on gene families and label co-occurrances
        """
        completed_network = deepcopy(network)

        gene_family_only, gene_both = {}, {}
        for node in completed_network["nodes"]:
            if "data" in node.keys() and "gene_id" in node["data"].keys():
                fam_only, both = [], []
                if "family_name" in node["data"]:
                    fam_only += [node["data"]["family_name"]]
                    both += [node["data"]["family_name"]]
                if "interpro" in node["data"]:
                    both += node["data"]["interpro"]
                gene_family_only[node["data"]["gene_id"]] = set(fam_only)
                gene_both[node["data"]["gene_id"]] = set(both)

        fam_to_shape_and_color = family_to_shape_and_color(gene_family_only)
        both_to_shape_and_color = family_to_shape_and_color(gene_both)

        for node in completed_network["nodes"]:
            if "data" in node.keys() and "gene_id" in node["data"].keys():
                if node["data"]["gene_id"] in fam_to_shape_and_color:
                    node["data"]["family_color"] = fam_to_shape_and_color[node["data"]["gene_id"]][1]
                    node["data"]["family_shape"] = fam_to_shape_and_color[node["data"]["gene_id"]][0]
                if node["data"]["gene_id"] in both_to_shape_and_color:
                    node["data"]["lc_color"] = both_to_shape_and_color[node["data"]["gene_id"]][1]
                    node["data"]["lc_shape"] = both_to_shape_and_color[node["data"]["gene_id"]][0]

        return completed_network

    @staticmethod
    def add_descriptions_nodes(network):
        completed_network = deepcopy(network)

        sequence_ids = []
        for node in completed_network["nodes"]:
            if "data" in node.keys() and "gene_id" in node["data"].keys():
                sequence_ids.append(node["data"]["gene_id"])

        sequences = Sequence.query.filter(Sequence.id.in_(sequence_ids)).all()

        descriptions = {s.id: s.description for s in sequences}
        tokens = {s.id: ", ".join([x.name for x in s.xrefs if x.platform == 'token']) for s in sequences}

        # Set empty tokens to None
        for k, v in tokens.items():
            if v == "":
                tokens[k] = None

        for node in completed_network["nodes"]:
            if "data" in node.keys() and "gene_id" in node["data"].keys():
                if node["data"]["gene_id"] in descriptions.keys():
                    node["data"]["description"] = descriptions[node["data"]["gene_id"]]
                else:
                    node["data"]["description"] = None

                if node["data"]["gene_id"] in tokens.keys():
                    node["data"]["tokens"] = tokens[node["data"]["gene_id"]]
                else:
                    node["data"]["tokens"] = None

        return completed_network

    @staticmethod
    def add_depth_data_nodes(network):
        """
        Colors a cytoscape compatible network (dict) based on edge depth

        This function is no longer used as it has been replaced by a mapper in the cycss

        :param network: dict containing the network
        :return: Cytoscape.js compatible network with depth information for nodes added
        """
        colored_network = deepcopy(network)

        colors = ["#3CE500", "#B7D800", "#CB7300", "#BF0003"]

        for node in colored_network["nodes"]:
            if "data" in node.keys() and "depth" in node["data"].keys():
                node["data"]["depth_color"] = colors[node["data"]["depth"]]

        return colored_network

    @staticmethod
    def add_connection_data_nodes(network):
        """
        A data to cytoscape compatible network's nodes based on the number of edges that node possesses

        :param network: dict containing the network
        :return: Cytoscape.js compatible network with connectivity information for nodes added
        """
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
    def add_depth_data_edges(network):
        """
        Colors a cytoscape compatible network (dict) based on edge depth

        This function is no longer used as it has been replaced by a mapper in the cycss

        :param network: dict containing the network
        :return: Cytoscape.js compatible network with depth information for edges added
        """
        colored_network = deepcopy(network)

        colors = ["#3CE500", "#B7D800", "#CB7300", "#BF0003"]

        for edge in colored_network["edges"]:
            if "data" in edge.keys() and "depth" in edge["data"].keys():
                edge["data"]["depth_color"] = colors[edge["data"]["depth"]]

        return colored_network

    @staticmethod
    def merge_networks(network_one, network_two):
        """
        Function to merge two networks. A compound/parent node is created for each network and based on the family_id,
        edges between homologous/orthologous genes are added.

        Note that label co-occurrences need to be (re-)calculated on the merged network

        :param network_one: Dictionary (cytoscape.js structure) of the first network
        :param network_two: Dictionary (cytoscape.js structure) of the second network
        :return: Cytoscape.js compatible network with both networks merged and homologs/orthologs connected
        """
        nodes = []
        edges = network_one['edges'] + network_two['edges']

        nodes.append({"data": {"id": "compound_node_one", "compound": True, "color": "#BEF"}})
        nodes.append({"data": {"id": "compound_node_two", "compound": True, "color": "#BEF"}})

        for node in network_one["nodes"]:
            node["data"]["parent"] = "compound_node_one"
            nodes.append(node)

        for node in network_two["nodes"]:
            node["data"]["parent"] = "compound_node_two"
            nodes.append(node)

        # draw edges between nodes from different networks
        # TODO: optimize this to avoid nested loop
        for node_one in network_one["nodes"]:
            for node_two in network_two["nodes"]:
                # if nodes are from the same family add an edge between them
                if node_one["data"]["family_id"] is not None \
                        and node_one["data"]["family_id"] == node_two["data"]["family_id"]:
                    edges.append({'data': {'source': node_one["data"]["id"],
                                           'target': node_two["data"]["id"],
                                           'color': "#33D",
                                           'homology': True}})

        return {'nodes': nodes, 'edges': edges}

    @staticmethod
    def get_families(network):
        return [f["data"]["family_name"] for f in network["nodes"] if 'data' in f.keys() and
                'family_name' in f["data"].keys() and
                f["data"]["family_name"] is not None]
