from flask import request, flash, url_for
from conekt.extensions import admin_required
from werkzeug.exceptions import abort
from werkzeug.utils import redirect

from conekt.controllers.admin.controls import admin_controls
from conekt.forms.admin.add_expression_specificity import AddConditionSpecificityForm, AddTissueSpecificityForm
from conekt.models.condition_tissue import ConditionTissue
from conekt.models.expression.specificity import ExpressionSpecificityMethod


@admin_controls.route('/add/condition_specificity', methods=['POST'])
@admin_required
def add_condition_specificity():
    form = AddConditionSpecificityForm(request.form)
    form.populate_species()

    if request.method == 'POST' and form.validate():
        species_id = int(request.form.get('species_id'))
        description = request.form.get('description')

        ExpressionSpecificityMethod.calculate_specificities(species_id, description, False)

        flash('Calculated condition specificities for species %d' % species_id, 'success')
        return redirect(url_for('admin.index'))
    else:
        if not form.validate():
            flash('Unable to validate data, potentially missing fields', 'danger')
            return redirect(url_for('admin.index'))
        else:
            abort(405)


@admin_controls.route('/add/tissue_specificity', methods=['POST'])
@admin_required
def add_tissue_specificity():
    form = AddTissueSpecificityForm(request.form)
    form.populate_species()

    if request.method == 'POST' and form.validate():
        species_id = int(request.form.get('species_id'))
        description = request.form.get('description')

        file = request.files[form.file.name].read()

        if file != b'':
            data = file.decode("utf-8").replace("\r\n", "\n").split('\n')

            order = []
            colors = []
            conditions = []

            condition_tissue = {}

            for d in data:
                condition, tissue, color = d.split("\t")

                conditions.append(condition)

                condition_tissue[condition] = tissue

                if tissue not in order:
                    order.append(tissue)
                    colors.append(color)

            specificity_method_id = ExpressionSpecificityMethod.calculate_tissue_specificities(species_id, description,
                                                                                               condition_tissue,
                                                                                               conditions,
                                                                                               use_max=True,
                                                                                               remove_background=False)
            ConditionTissue.add(species_id, condition_tissue, order, colors, specificity_method_id)

        flash('Calculated tissue specificities for species %d' % species_id, 'success')
        return redirect(url_for('admin.index'))
    else:
        if not form.validate():
            flash('Unable to validate data, potentially missing fields', 'danger')
            return redirect(url_for('admin.index'))
        else:
            abort(405)