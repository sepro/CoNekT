from flask import Blueprint, url_for, render_template, flash, redirect

from planet.models.coexpression_clusters import CoexpressionCluster, CoexpressionClusteringMethod
from planet.models.coexpression_clusters_cytoscape import CoexpressionClusterCytoscape

from utils.benchmark import benchmark

import json


expression_cluster = Blueprint('expression_cluster', __name__)


@expression_cluster.route('/')
def expression_cluster_overview():
    """
    Overview of all networks in the current database with basic information
    """
    cluster_methods = CoexpressionClusteringMethod.query.all()

    return render_template("expression_cluster.html", cluster_methods=cluster_methods)


@expression_cluster.route('/view/<cluster_id>')
def expression_cluster_view(cluster_id):
    output = CoexpressionClusterCytoscape.get_cluster(cluster_id)

    return json.dumps(output)
