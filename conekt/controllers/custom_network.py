import json

from flask import Blueprint, request, render_template, Response, Markup

from conekt.forms.custom_network import CustomNetworkForm
from conekt.helpers.cytoscape import CytoscapeHelper
from conekt.models.expression.networks import ExpressionNetwork, ExpressionNetworkMethod
from conekt.models.sequences import Sequence

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

        family_method_id = request.form.get('family_method')
        cluster_method_id = request.form.get('cluster_method')
        specificity_method_id = request.form.get('specificity_method')

        probes = terms

        # also do search by gene ID
        sequences = Sequence.query.filter(Sequence.name.in_(terms)).all()

        for s in sequences:
            for ep in s.expression_profiles:
                probes.append(ep.probe)

        # make probe list unique
        probes = list(set(probes))

        network_method = ExpressionNetworkMethod.query.get_or_404(method_id)
        network = ExpressionNetwork.get_custom_network(method_id, probes)

        network_cytoscape = CytoscapeHelper.parse_network(network)
        network_cytoscape = CytoscapeHelper.add_family_data_nodes(network_cytoscape, family_method_id)
        network_cytoscape = CytoscapeHelper.add_lc_data_nodes(network_cytoscape)
        network_cytoscape = CytoscapeHelper.add_descriptions_nodes(network_cytoscape)
        network_cytoscape = CytoscapeHelper.add_cluster_data_nodes(network_cytoscape, cluster_method_id)
        network_cytoscape = CytoscapeHelper.add_specificity_data_nodes(network_cytoscape, specificity_method_id)

        return render_template("expression_graph.html", graph_data=Markup(json.dumps(network_cytoscape)),
                               cutoff=network_method.hrr_cutoff)
    else:

        example = {
            'method_id': None,
            'probes': None
        }

        data = ExpressionNetwork.query.order_by(ExpressionNetwork.method_id).limit(20).all()

        probes = []

        for d in data:
            example['method_id'] = d.method_id

            if d.probe not in probes:
                probes.append(d.probe)

            network = json.loads(d.network)
            for n in network:
                if "gene_name" in n and "gene_name" not in probes and len(probes) < 35:
                    probes.append(n["gene_name"])

            if len(probes) >= 35:
                break
        example['probes'] = ' '.join(probes)

        return render_template("custom_network.html", form=form, example=example)


@custom_network.route('/form_data')
def custom_network_form_data():
    """
    Returns a JSON object with valid options for

    :return: JSON object with network methods and associated clustering methods and specificity methods
    """

    output = []

    network_methods = ExpressionNetworkMethod.query.all()

    for nm in network_methods:
        output.append({
            'id': nm.id,
            'name': nm.species.name + ' (' + nm.description + ')',
            'clustering_methods': [{'id': c.id, 'method': c.method} for c in nm.clustering_methods],
            'species': nm.species.name,
            'specificity_methods': [{'id': es.id, 'method': es.description} for es in nm.species.expression_specificities]
        })

    return Response(json.dumps(output), mimetype='application/json')


@custom_network.route('/json', methods=['POST'])
def custom_network_json():
    """
    Profile comparison tool, accepts a species and a list of probes and plots the profiles for the selected
    """
    terms = request.form.get('probes').split()
    method_id = request.form.get('method_id')

    family_method_id = request.form.get('family_method')
    cluster_method_id = request.form.get('cluster_method')
    specificity_method_id = request.form.get('specificity_method')

    probes = terms

    # also do search by gene ID
    sequences = Sequence.query.filter(Sequence.name.in_(terms)).all()

    for s in sequences:
        for ep in s.expression_profiles:
            probes.append(ep.probe)

    # make probe list unique
    probes = list(set(probes))

    network = ExpressionNetwork.get_custom_network(method_id, probes)

    network_cytoscape = CytoscapeHelper.parse_network(network)
    network_cytoscape = CytoscapeHelper.add_family_data_nodes(network_cytoscape, family_method_id)
    network_cytoscape = CytoscapeHelper.add_lc_data_nodes(network_cytoscape)
    network_cytoscape = CytoscapeHelper.add_descriptions_nodes(network_cytoscape)
    network_cytoscape = CytoscapeHelper.add_cluster_data_nodes(network_cytoscape, cluster_method_id)
    network_cytoscape = CytoscapeHelper.add_specificity_data_nodes(network_cytoscape, specificity_method_id)

    return Response(json.dumps(network_cytoscape), mimetype='application/json')

