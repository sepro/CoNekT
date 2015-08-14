import json
from flask import url_for
from planet import ExpressionNetwork
from sqlalchemy import and_


class ExpressionNetworkCytoscape(ExpressionNetwork):
    @staticmethod
    def get_neighborhood(probe, depth=0):
        node = ExpressionNetworkCytoscape.query.get(probe)
        links = json.loads(node.network)

        method_id = node.method_id

        # add the initial node
        nodes = [{"data": {"id": node.probe,
                           "name": node.probe,
                           "gene_link": url_for('sequence.sequence_view', sequence_id=node.gene_id),
                           "gene_name": node.gene.name,
                           "node_type": "query",
                           "color": "#888"}}]
        edges = []

        # lists necessary for doing deeper searches
        additional_nodes = []
        existing_edges = []
        existing_nodes = [node.probe]

        # add direct neighbors of the gene of interest

        for link in links:
            nodes.append(ExpressionNetworkCytoscape.__process_link(link))
            edges.append({"data": {"source": node.probe,
                                   "target": link["probe_name"],
                                   "depth": 0,
                                   "link_score": link["link_score"],
                                   "color": "#CCC"}})
            additional_nodes.append(link["probe_name"])
            existing_edges.append([node.probe, link["probe_name"]])
            existing_edges.append([link["probe_name"], node.probe])
            existing_nodes.append(link["probe_name"])

        # iterate n times to add deeper links

        for i in range(1, depth+1):
            new_nodes = ExpressionNetworkCytoscape.query.filter(and_(ExpressionNetworkCytoscape.probe.in_(additional_nodes),
                                                            ExpressionNetworkCytoscape.method_id == method_id))
            next_nodes = []

            for new_node in new_nodes:
                new_links = json.loads(new_node.network)

                for link in new_links:
                    if link["probe_name"] not in existing_nodes:
                        nodes.append(ExpressionNetworkCytoscape.__process_link(link))
                        existing_nodes.append(link["probe_name"])
                        next_nodes.append(link["probe_name"])

                    if [new_node.probe, link["probe_name"]] not in existing_edges:
                        edges.append({"data": {"source": new_node.probe,
                                               "target": link["probe_name"],
                                               "depth": i,
                                               "link_score": link["link_score"],
                                               "color": "#CCC"}})
                        existing_edges.append([new_node.probe, link["probe_name"]])
                        existing_edges.append([link["probe_name"], new_node.probe])

            additional_nodes = next_nodes

        # Add links between the last set of nodes added
        new_nodes = ExpressionNetworkCytoscape.query.filter(and_(ExpressionNetworkCytoscape.probe.in_(additional_nodes),
                                                        ExpressionNetworkCytoscape.method_id == method_id))
        for new_node in new_nodes:
            new_links = json.loads(new_node.network)
            for link in new_links:
                if link["probe_name"] in existing_nodes:
                    if [new_node.probe, link["probe_name"]] not in existing_edges:
                        edges.append({"data": {"source": new_node.probe,
                                               "target": link["probe_name"],
                                               "depth": depth+1,
                                               "link_score": link["link_score"],
                                               "color": "#CCC"}})
                        existing_edges.append([new_node.probe, link["probe_name"]])
                        existing_edges.append([link["probe_name"], new_node.probe])

        return {"nodes": nodes, "edges": edges}

    @staticmethod
    def __process_link(linked_probe):
        """
        Internal function that processes a linked probe (from the ExpressionNetwork.network field) to a data entry
        compatible with cytoscape.js

        :param linked_probe: hash with information from ExpressionNetwork.network field
        :return: a hash formatted for use as a node with cytoscape.js
        """
        if linked_probe["gene_id"] is not None:
            return {"data": {"id": linked_probe["probe_name"],
                             "name": linked_probe["probe_name"],
                             "gene_link": url_for('sequence.sequence_view', sequence_id=linked_probe["gene_id"]),
                             "gene_name": linked_probe["gene_name"],
                             "node_type": "linked",
                             "color": "#888"}}
        else:
            return {"data": {"id": linked_probe["probe_name"],
                             "name": linked_probe["probe_name"],
                             "gene_link": url_for('sequence.sequence_view', sequence_id=""),
                             "gene_name": linked_probe["gene_name"],
                             "node_type": "linked",
                             "color": "#888"}}