import os
from tempfile import mkstemp

from flask import request, flash, url_for
from flask_login import login_required
from werkzeug.exceptions import abort
from werkzeug.utils import redirect

from planet.controllers.admin.controls import admin_controls
from planet.forms.admin.add_sequence_descriptions import AddSequenceDescriptionsForm
from planet.models.sequences import Sequence


@admin_controls.route('/add/sequence_descriptions', methods=['POST'])
@login_required
def add_descriptions():
    form = AddSequenceDescriptionsForm(request.form)

    if request.method == 'POST':
        species_id = int(request.form.get('species_id'))

        description_data = request.files[form.file.name].read()
        if description_data != b'':
            fd, temp_path = mkstemp()

            with open(temp_path, 'wb') as desc_writer:
                desc_writer.write(description_data)

            Sequence.add_descriptions(temp_path, species_id)

            os.close(fd)
            os.remove(temp_path)
            flash('Added descriptions from file %s' % form.file.name, 'success')
        else:
            flash('Empty file or no file provided, cannot add descriptions', 'danger')

        return redirect(url_for('admin.index'))
    else:
        if not form.validate():
            flash('Unable to validate data, potentially missing fields', 'danger')
            return redirect(url_for('admin.index'))
        else:
            abort(405)