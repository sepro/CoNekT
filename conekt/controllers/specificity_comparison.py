from flask import Blueprint, request, render_template

from conekt.forms.compare_specificity import CompareSpecificityForm
from conekt.models.expression.specificity import ExpressionSpecificityMethod
from conekt.models.species import Species
from conekt.models.expression.specificity_comparison import SpecificityComparison

specificity_comparison = Blueprint('specificity_comparison', __name__)


@specificity_comparison.route('/', methods=['GET', 'POST'])
def specificity_comparison_main():
    """
    For to compare tissue/condition specific gene across species

    :return: search form (GET) or results (POST)
    """
    form = CompareSpecificityForm(request.form)
    form.populate_form()

    if request.method == 'GET':
        return render_template('compare_specificity.html', form=form)
    else:
        family_method = request.form.get('family_method')

        use_interpro = request.form.get('use_interpro') == 'y'

        species_a_id = request.form.get('speciesa')
        method_a_id = request.form.get('methodsa')
        condition_a = request.form.get('conditionsa')
        cutoff_a = request.form.get('cutoffa')

        species_b_id = request.form.get('speciesb')
        method_b_id = request.form.get('methodsb')
        condition_b = request.form.get('conditionsb')
        cutoff_b = request.form.get('cutoffb')

        # Check if things that should exist do
        species_a = Species.query.get_or_404(species_a_id)
        method_a = ExpressionSpecificityMethod.query.get_or_404(method_a_id)
        species_b = Species.query.get_or_404(species_b_id)
        method_b = ExpressionSpecificityMethod.query.get_or_404(method_b_id)

        counts, table_data = SpecificityComparison.get_specificity_comparison(method_a_id, method_b_id,
                                                                              cutoff_a, cutoff_b,
                                                                              condition_a, condition_b,
                                                                              use_interpro, family_method=family_method)

        return render_template('compare_specificity.html', counts=counts,
                               table_data=table_data,
                               labels={'left_species': species_a.name,
                                       'right_species': species_b.name,
                                       'left_method': method_a.description,
                                       'right_method': method_b.description,
                                       'left_condition': condition_a,
                                       'right_condition': condition_b},
                               use_interpro=use_interpro)
