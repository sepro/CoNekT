from flask import Blueprint, current_app, Response, redirect, url_for, request, render_template, flash
from flask_login import login_required

from planet.models.coexpression_clusters import CoexpressionClusteringMethod
from planet.models.expression_networks import ExpressionNetworkMethod
from planet.models.gene_families import GeneFamilyMethod
from planet.models.species import Species
from planet.models.clades import Clade

import json

admin_controls = Blueprint('admin_controls', __name__)


@admin_controls.route('/')
@login_required
def main():
    flash('TEST Success', 'success')

    return redirect(url_for('main.screen'))


@admin_controls.route('/update/counts')
@login_required
def update_counts():
    try:
        CoexpressionClusteringMethod.update_counts()
        ExpressionNetworkMethod.update_count()
        GeneFamilyMethod.update_count()
        Species.update_counts()
    except:
        return Response(json.dumps({'status': 'failed', 'message': 'Unable to update counts'}))
    else:
        return Response(json.dumps({'status': 'success', 'message': 'Updated all counts'}))


@admin_controls.route('/update/clades')
@login_required
def update_clades():
    try:
        Clade.update_clades()
        Clade.update_clades_interpro()
    except:
        return Response(json.dumps({'status': 'failed', 'message': 'Unable to update clades'}))
    else:
        return Response(json.dumps({'status': 'success', 'message': 'Updated all clades'}))