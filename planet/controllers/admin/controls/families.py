import os
from tempfile import mkstemp

from flask import request, flash, url_for
from flask_login import login_required
from werkzeug.exceptions import abort
from werkzeug.utils import redirect

from planet.controllers.admin.controls import admin_controls
from planet.forms.admin.add_family import AddFamiliesForm
from planet.models.gene_families import GeneFamily


@admin_controls.route('/add/family', methods=['POST'])
@login_required
def add_family():
    """
    Add gene families to PlaNet from various sources.

    :return: Redirect to admin panel interface:
    """
    form = AddFamiliesForm(request.form)

    if request.method == 'POST':
        method_description = request.form.get('method_description')
        source = request.form.get('source')

        family_data = request.files[form.file.name].read()
        if family_data != b'':
            fd, temp_path = mkstemp()

            with open(temp_path, 'wb') as family_writer:
                family_writer.write(family_data)

            if source == 'mcl':
                GeneFamily.add_families_from_mcl(temp_path, method_description)
                flash('Added Gene families from file %s' % form.file.name, 'success')
            elif source == 'orthofinder':
                GeneFamily.add_families_from_orthofinder(temp_path, method_description)
                flash('Added Gene families from file %s' % form.file.name, 'success')
            else:
                flash('Method not implemented yet', 'danger')
            os.close(fd)
            os.remove(temp_path)

        else:
            flash('Empty file or no file provided, cannot add gene families', 'warning')

        return redirect(url_for('admin.index'))
    else:
        if not form.validate():
            flash('Unable to validate data, potentially missing fields', 'danger')
            return redirect(url_for('admin.index'))
        else:
            abort(405)