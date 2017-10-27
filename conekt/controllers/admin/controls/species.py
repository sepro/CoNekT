import os
from tempfile import mkstemp

from flask import request, flash, url_for
from conekt.extensions import admin_required
from werkzeug.exceptions import abort
from werkzeug.utils import redirect

from conekt.controllers.admin.controls import admin_controls
from conekt.forms.admin.add_species import AddSpeciesForm
from conekt.models.sequences import Sequence
from conekt.models.species import Species


@admin_controls.route('/add/species', methods=['POST'])
@admin_required
def add_species():
    """
    Adds a species to the species table and adds sequences for that species to the sequence table based on the fasta
    file provided.

    :return: Redirect to admin panel interface
    """
    form = AddSpeciesForm(request.form)

    if request.method == 'POST' and form.validate():
        # Add species (or return id of existing species)
        species_id = Species.add(request.form.get('code'),
                                 request.form.get('name'),
                                 data_type=request.form.get('data_type'),
                                 color='#' + request.form.get('color'),
                                 highlight='#' + request.form.get('highlight'),
                                 description=request.form.get('description'))

        # Add Sequences
        fd, temp_path = mkstemp()

        fasta_data = request.files[form.fasta.name].read()

        print(request.files[form.fasta.name].content_type)

        compressed = 'gzip' in request.files[form.fasta.name].content_type

        with open(temp_path, 'wb') as fasta_writer:
            fasta_writer.write(fasta_data)
        sequence_count = Sequence.add_from_fasta(temp_path, species_id, compressed=compressed)

        os.close(fd)
        os.remove(temp_path)
        flash('Added species %s with %d sequences' % (request.form.get('name'), sequence_count), 'success')
        return redirect(url_for('admin.index'))
    else:
        if not form.validate():
            flash('Unable to validate data, potentially missing fields', 'danger')
            return redirect(url_for('admin.index'))
        else:
            abort(405)
