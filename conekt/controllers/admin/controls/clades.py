import json

from flask import flash, url_for, request, Markup
from conekt.extensions import admin_required
from werkzeug.exceptions import abort
from werkzeug.utils import redirect

from conekt.controllers.admin.controls import admin_controls
from conekt.forms.admin.add_clades import AddCladesForm
from conekt.models.clades import Clade
from conekt.models.expression.coexpression_clusters import CoexpressionCluster


@admin_controls.route('/update/clades')
@admin_required
def update_clades():
    """
    Controller that will update the clade information for gene families and interpro domains. It will detect in which
    clade a family/domain originated and add that info to the database.

    :return: Redirect to admin panel interface
    """
    try:
        Clade.update_clades()
        Clade.update_clades_interpro()
    except Exception as e:
        flash('An error occurred while updating clades', 'danger')
    else:
        flash('All clades updated', 'success')

    return redirect(url_for('admin.index'))


@admin_controls.route('/add/clades', methods=['POST'])
@admin_required
def add_clades():
    """
    Adds clades to the database based on a structured JSON object.

    :return: Redirect to admin panel interface
    """
    form = AddCladesForm(request.form)

    if request.method == 'POST' and form.validate():
        clades_json = json.loads(request.form.get('clades_json'))

        Clade.add_clades_from_json(clades_json)

        flash('Added clades %s to the database' % ', '.join(clades_json.keys()), 'success')
        return redirect(url_for('admin.index'))
    else:
        if not form.validate():
            flash('Unable to validate data, potentially missing fields', 'danger')
            return redirect(url_for('admin.index'))
        else:
            abort(405)


@admin_controls.route('/calculate_clade_enrichment/<int:gf_method_id>')
@admin_required
def calculate_clade_enrichment(gf_method_id):
    """
    Controller to start GO enrichment calculations

    :return: Redirect to admin main screen
    """
    try:
        CoexpressionCluster.calculate_clade_enrichment(gf_method_id)
    except Exception as e:
        flash(Markup('An error occurred! Please ensure the file is <strong>correctly formatted</strong>' +
                     ' and <strong>update the counts</strong> if necessary'), 'warning')
    finally:
        flash('Successfully calculated clade enrichment for co-expression clusters', 'success')

    return redirect(url_for('admin.controls.index'))
