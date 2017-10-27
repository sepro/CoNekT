import os
from tempfile import mkstemp

from flask import request, flash, url_for
from conekt.extensions import admin_required
from werkzeug.exceptions import abort
from werkzeug.utils import redirect

from conekt.controllers.admin.controls import admin_controls
from conekt.forms.admin.add_coexpression_clusters import AddCoexpressionClustersForm
from conekt.forms.admin.build_coexpression_clusters import BuildCoexpressionClustersForm
from conekt.forms.admin.neighborhood_to_clusters import NeighborhoodToClustersForm
from conekt.models.expression.coexpression_clusters import CoexpressionClusteringMethod, CoexpressionCluster
from conekt.models.relationships.cluster_similarity import CoexpressionClusterSimilarity


@admin_controls.route('/build/neighborhoods_to_clusters', methods=['POST'])
@admin_required
def neighborhoods_to_clusters():
    form = NeighborhoodToClustersForm(request.form)
    form.populate_networks()
    if request.method == 'POST' and form.validate():
        network_method_id = int(request.form.get('network_id'))
        description = request.form.get('description')
        CoexpressionClusteringMethod.clusters_from_neighborhoods(description, network_method_id)

        flash('Succesfully build clusters from neighborhoods.', 'success')
        return redirect(url_for('admin.index'))
    else:
        if not form.validate():
            flash('Unable to validate data, potentially missing fields', 'danger')
            return redirect(url_for('admin.index'))
        else:
            abort(405)


@admin_controls.route('/build/hcca_clusters', methods=['POST'])
@admin_required
def build_hcca_clusters():
    """
    Controller that will start building HCCA clusters for a selected network

    :return: return to admin index
    """
    form = BuildCoexpressionClustersForm(request.form)
    form.populate_networks()
    if request.method == 'POST' and form.validate():
        network_method_id = int(request.form.get('network_id'))
        description = request.form.get('description')
        CoexpressionClusteringMethod.build_hcca_clusters(description, network_method_id)

        flash('Succesfully build clusters using HCCA.', 'success')
        return redirect(url_for('admin.index'))
    else:
        if not form.validate():
            flash('Unable to validate data, potentially missing fields', 'danger')
            return redirect(url_for('admin.index'))
        else:
            abort(405)


@admin_controls.route('/add/coexpression_clusters', methods=['POST'])
@admin_required
def add_coexpression_clusters():
    """
    Add co-expression clusters, based on LSTrAP output (MCL clusters)

    :return: Redirect to admin panel interface
    """
    form = AddCoexpressionClustersForm(request.form)
    form.populate_networks()

    if request.method == 'POST' and form.validate():
        network_id = int(request.form.get('network_id'))
        description = request.form.get('description')
        min_size = int(request.form.get('min_size'))

        file = request.files[form.file.name].read()

        if file != b'':
            fd, temp_path = mkstemp()

            with open(temp_path, 'wb') as cluster_writer:
                cluster_writer.write(file)

            CoexpressionClusteringMethod.add_lstrap_coexpression_clusters(temp_path, description, network_id,
                                                                          min_size=min_size)

            os.close(fd)
            os.remove(temp_path)
            flash('Added coexpression clusters for network method %d' % network_id, 'success')
        else:
            flash('Empty or no file provided, cannot add coexpression network', 'warning')

        return redirect(url_for('admin.index'))
    else:
        if not form.validate():
            flash('Unable to validate data, potentially missing fields', 'danger')
            return redirect(url_for('admin.index'))
        else:
            abort(405)


@admin_controls.route('/calculate_cluster_similarity/<int:gf_method_id>')
@admin_required
def calculate_cluster_similarity(gf_method_id):
    """
    Calculate similarities between co-expression clusterings based on content. Homologous genes are used to indicate the
    similarity.

    :param gf_method_id: gene family method to use for similarities
    :return: Redirect to admin main screen
    """
    CoexpressionCluster.calculate_similarities(gene_family_method_id=gf_method_id)

    flash('Successfully calculated co-expression clustering similarities', 'success')
    return redirect(url_for('admin.controls.index'))


@admin_controls.route('/delete_cluster_similarity')
@admin_required
def delete_cluster_similarity():
    """
    Controller to delete all existing cluster cluster similarities

    :return: Redirect to admin main screen
    """
    CoexpressionClusterSimilarity.empty_table()

    flash('Successfully removed similarities between co-expression clusters', 'success')
    return redirect(url_for('admin.controls.index'))