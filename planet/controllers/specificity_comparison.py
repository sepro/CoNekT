from collections import defaultdict

from flask import Blueprint, request, render_template

from planet.forms.compare_specificity import CompareSpecificityForm
from planet.models.expression.specificity import ExpressionSpecificityMethod, ExpressionSpecificity
from planet.models.relationships import SequenceFamilyAssociation
from planet.models.species import Species

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

        # Fetch results
        results_a = ExpressionSpecificity.query.filter_by(method_id=method_a_id, condition=condition_a).filter(ExpressionSpecificity.score>=cutoff_a)
        results_b = ExpressionSpecificity.query.filter_by(method_id=method_b_id, condition=condition_b).filter(ExpressionSpecificity.score>=cutoff_b)

        sequence_ids = [r.profile.sequence_id for r in results_a] + [r.profile.sequence_id for r in results_b]

        family_associations = SequenceFamilyAssociation.query.filter(SequenceFamilyAssociation.family.has(method_id=1)).filter(SequenceFamilyAssociation.sequence_id.in_(sequence_ids))
        seq_to_fam = {f.sequence_id: f.gene_family_id for f in family_associations}
        fam_to_data = defaultdict(list)
        famID_to_name = {}

        for f in family_associations:
            fam_to_data[f.gene_family_id].append({'id': f.sequence_id, 'name': f.sequence.name})
            famID_to_name[f.gene_family_id] = f.family.name

        families_a = set([seq_to_fam[r.profile.sequence_id] for r in results_a if r.profile.sequence_id in seq_to_fam.keys()])
        families_b = set([seq_to_fam[r.profile.sequence_id] for r in results_b if r.profile.sequence_id in seq_to_fam.keys()])

        a_only = [{'id': f, 'name': famID_to_name[f], 'sequences': fam_to_data[f]} for f in families_a.difference(families_b)]
        intersection = [{'id': f, 'name': famID_to_name[f],  'sequences': fam_to_data[f]} for f in families_a.intersection(families_b)]
        b_only = [{'id': f, 'name': famID_to_name[f], 'sequences': fam_to_data[f]} for f in families_b.difference(families_a)]

        return render_template('compare_specificity.html', a_only=a_only, b_only=b_only, intersection=intersection,
                               labels={'left_species': species_a.name,
                                        'right_species': species_b.name,
                                        'left_method': method_a.description,
                                        'right_method': method_b.description,
                                        'left_condition': condition_a,
                                        'right_condition': condition_b})