import os
from tempfile import mkstemp

from flask import request, flash, url_for
from conekt.extensions import admin_required
from werkzeug.exceptions import abort
from werkzeug.utils import redirect

from conekt.controllers.admin.controls import admin_controls
from conekt.forms.admin.add_expression_profiles import AddExpressionProfilesForm
from conekt.models.expression.profiles import ExpressionProfile


@admin_controls.route('/add/expression_profile', methods=['POST'])
@admin_required
def add_expression_profiles():
    """
    Add expression profiles to sequences based on data from LSTrAP

    :return: Redirect to admin panel interface
    """
    form = AddExpressionProfilesForm(request.form)

    if request.method == 'POST':
        species_id = int(request.form.get('species_id'))
        source = request.form.get('source')

        matrix_file = request.files[form.matrix_file.name].read()
        annotation_file = request.files[form.annotation_file.name].read()
        order_colors_file = request.files[form.order_colors_file.name].read()
        if matrix_file != b'' and annotation_file != b'':
            fd_matrix, temp_matrix_path = mkstemp()

            with open(temp_matrix_path, 'wb') as matrix_writer:
                matrix_writer.write(matrix_file)

            fd_annotation, temp_annotation_path = mkstemp()
            with open(temp_annotation_path, 'wb') as annotation_writer:
                annotation_writer.write(annotation_file)

            if order_colors_file != b'':
                fd_order_colors, temp_order_colors_path = mkstemp()
                with open(temp_order_colors_path, 'wb') as oc_writer:
                    oc_writer.write(order_colors_file)

                ExpressionProfile.add_profile_from_lstrap(temp_matrix_path, temp_annotation_path, species_id,
                                                          order_color_file=temp_order_colors_path)

                os.close(fd_order_colors)
                os.remove(temp_order_colors_path)
            else:
                ExpressionProfile.add_profile_from_lstrap(temp_matrix_path, temp_annotation_path, species_id)

            os.close(fd_annotation)
            os.remove(temp_annotation_path)
            os.close(fd_matrix)
            os.remove(temp_matrix_path)

            flash('Added expression profiles for species %d' % species_id, 'success')
        else:
            flash('Empty file or no file provided, cannot add gene families', 'warning')
        return redirect(url_for('admin.index'))
    else:
        if not form.validate():
            flash('Unable to validate data, potentially missing fields', 'danger')
            return redirect(url_for('admin.index'))
        else:
            abort(405)