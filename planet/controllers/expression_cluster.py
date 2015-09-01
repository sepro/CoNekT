from flask import Blueprint, url_for, render_template, flash, redirect

from planet.models.coexpression_clusters import CoexpressionCluster, CoexpressionClusteringMethod

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



