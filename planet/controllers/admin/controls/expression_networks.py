import os
from tempfile import mkstemp

from flask import request, flash, url_for
from planet.extensions import admin_required
from werkzeug.exceptions import abort
from werkzeug.utils import redirect

from planet.controllers.admin.controls import admin_controls
from planet.forms.admin.add_coexpression_network import AddCoexpressionNetworkForm
from planet.models.expression.networks import ExpressionNetwork


@admin_controls.route('/add/coexpression_network', methods=['POST'])
@admin_required
def add_coexpression_network():
    """
    Adds the co-expression network for a species based on LSTrAP output

    :return: Redirect to admin panel interface
    """
    form = AddCoexpressionNetworkForm(request.form)

    if request.method == 'POST':
        species_id = int(request.form.get('species_id'))
        description = request.form.get('description')
        limit = int(request.form.get('limit'))
        pcc_cutoff = float(request.form.get('pcc_cutoff'))
        enable_second_level = True if request.form.get('enable_second_level') == 'y' else False

        file = request.files[form.file.name].read()

        if file != b'':
            fd, temp_path = mkstemp()
            with open(temp_path, 'wb') as network_writer:
                network_writer.write(file)

            ExpressionNetwork.read_expression_network_lstrap(temp_path, species_id, description,
                                                             pcc_cutoff=pcc_cutoff,
                                                             limit=limit, enable_second_level=enable_second_level)

            os.close(fd)
            os.remove(temp_path)
            flash('Added coexpression network for species %d' % species_id, 'success')
        else:
            flash('Empty or no file provided, cannot add coexpression network', 'warning')

        return redirect(url_for('admin.index'))
    else:
        if not form.validate():
            flash('Unable to validate data, potentially missing fields', 'danger')
            return redirect(url_for('admin.index'))
        else:
            abort(405)