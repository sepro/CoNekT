from flask import Blueprint, request, render_template, Response, Markup

from planet.models.expression_networks import ExpressionNetwork
from planet.models.sequences import Sequence
from planet.forms.custom_network import CustomNetworkForm

from planet.helpers.cytoscape import CytoscapeHelper

import json

custom_network = Blueprint('custom_network', __name__)


@custom_network.route('/', methods=['GET', 'POST'])
def custom_network_main():
    """
    Profile comparison tool, accepts a species and a list of probes and plots the profiles for the selected
    """
    form = CustomNetworkForm(request.form)
    form.populate_method()

    if request.method == 'POST':
        terms = request.form.get('probes').split()
        method_id = request.form.get('method_id')

        probes = terms

        # also do search by gene ID
        sequences = Sequence.query.filter(Sequence.name.in_(terms)).all()

        for s in sequences:
            for ep in s.expression_profiles:
                probes.append(ep.probe)

        #make probe list unique
        probes = list(set(probes))

        network = ExpressionNetwork.get_custom_network(method_id, probes)

        network_cytoscape = CytoscapeHelper.parse_network(network)
        network_cytoscape = CytoscapeHelper.add_family_data_nodes(network_cytoscape, 1)
        network_cytoscape = CytoscapeHelper.add_lc_data_nodes(network_cytoscape)
        network_cytoscape = CytoscapeHelper.add_descriptions_nodes(network_cytoscape)

        return render_template("expression_graph.html", graph_data=Markup(json.dumps(network_cytoscape)))
    else:
        return render_template("custom_network.html", form=form)


@custom_network.route('/json', methods=['POST'])
def custom_network_json():
    """
    Profile comparison tool, accepts a species and a list of probes and plots the profiles for the selected
    """
    probes = request.form.get('probes').split()
    method_id = request.form.get('method_id')

    network = ExpressionNetwork.get_custom_network(method_id, probes)

    network_cytoscape = CytoscapeHelper.parse_network(network)
    network_cytoscape = CytoscapeHelper.add_family_data_nodes(network_cytoscape, 1)
    network_cytoscape = CytoscapeHelper.add_lc_data_nodes(network_cytoscape)
    network_cytoscape = CytoscapeHelper.add_descriptions_nodes(network_cytoscape)

    return Response(json.dumps(network_cytoscape), mimetype='application/json')

