import json

from flask import flash, url_for, request
from planet.extensions import admin_required
from werkzeug.exceptions import abort
from werkzeug.utils import redirect

from planet.controllers.admin.controls import admin_controls
from planet.forms.admin.add_clades import AddCladesForm
from planet.models.clades import Clade


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