import os
from tempfile import mkstemp

from flask import request, flash, url_for
from flask_login import login_required
from werkzeug.exceptions import abort
from werkzeug.utils import redirect

from planet.controllers.admin.controls import admin_controls
from planet.forms.admin.add_trees import AddTreesForm


@admin_controls.route('/add/trees', methods=['POST'])
@login_required
def add_trees():
    form = AddTreesForm(request.form)

    if request.method == 'POST':
        flash('Method not implemented -- Nothing happened', 'danger')
        return redirect(url_for('admin.index'))
    else:
        if not form.validate():
            flash('Unable to validate data, potentially missing fields', 'danger')
            return redirect(url_for('admin.index'))
        else:
            abort(405)
