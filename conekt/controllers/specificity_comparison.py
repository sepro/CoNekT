from collections import defaultdict

from flask import Blueprint, request, render_template

from conekt.forms.compare_specificity import CompareSpecificityForm
from conekt.models.expression.specificity import ExpressionSpecificityMethod, ExpressionSpecificity
from conekt.models.relationships.sequence_family import SequenceFamilyAssociation
from conekt.models.relationships.sequence_interpro import SequenceInterproAssociation
from conekt.models.species import Species

from sqlalchemy.orm import joinedload

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

        # Fetch results
        results_a = ExpressionSpecificity.query.filter(ExpressionSpecificity.method_id == method_a_id). \
            filter(ExpressionSpecificity.score >= cutoff_a).\
            filter(ExpressionSpecificity.condition == condition_a). \
            options(
                joinedload(ExpressionSpecificity.profile).undefer("profile")
            ).\
            all()
        results_b = ExpressionSpecificity.query.filter(ExpressionSpecificity.method_id == method_b_id). \
            filter(ExpressionSpecificity.score >= cutoff_b).\
            filter(ExpressionSpecificity.condition == condition_b). \
            options(
                joinedload(ExpressionSpecificity.profile).undefer("profile")
            ). \
            all()

        sequence_ids = [r.profile.sequence_id for r in results_a] + [r.profile.sequence_id for r in results_b]

        counts = {
            'left': 0,
            'right': 0,
            'intersection': 0
        }

        table_data = {}

        if use_interpro:
            interpro_associations = SequenceInterproAssociation.query.\
                filter(SequenceInterproAssociation.sequence_id.in_(sequence_ids)).all()

            sequence_id_left = [r.profile.sequence_id for r in results_a if r.profile.sequence_id is not None]
            sequence_id_right = [r.profile.sequence_id for r in results_b if r.profile.sequence_id is not None]

            abundance = defaultdict(lambda: False)

            for r in results_a + results_b:
                if r.profile.sequence_id is not None:
                    abundance[r.profile.sequence_id] = r.profile.low_abundance

            interpro_id_to_name = {i.interpro_id: "%s (%s)" % (i.domain.label, i.domain.description if i.domain.description else "no description") for i in interpro_associations}

            for i in interpro_associations:
                if i.interpro_id not in table_data.keys():
                    table_data[i.interpro_id] = {'id': i.interpro_id,
                                                 'name': interpro_id_to_name[i.interpro_id],
                                                 'left_genes': [],
                                                 'right_genes': []}
                if i.sequence_id in sequence_id_left:
                    table_data[i.interpro_id]['left_genes'].append({'id': i.sequence_id,
                                                                    'name': i.sequence.name,
                                                                    'shortest_alias': i.sequence.shortest_alias,
                                                                    'low_abundance': abundance[i.sequence_id]})

                if i.sequence_id in sequence_id_right:
                    table_data[i.interpro_id]['right_genes'].append({'id': i.sequence_id,
                                                                     'name': i.sequence.name,
                                                                     'shortest_alias': i.sequence.shortest_alias,
                                                                     'low_abundance': abundance[i.sequence_id]})

                if len(table_data[i.interpro_id]['left_genes']) > 0 and len(table_data[i.interpro_id]['right_genes']) == 0:
                    table_data[i.interpro_id]['type'] = 'left'
                    counts['left'] += 1
                elif len(table_data[i.interpro_id]['right_genes']) > 0 and len(table_data[i.interpro_id]['left_genes']) == 0:
                    table_data[i.interpro_id]['type'] = 'right'
                    counts['right'] += 1
                else:
                    table_data[i.interpro_id]['type'] = 'intersection'
                    counts['intersection'] += 1

        else:
            family_associations = SequenceFamilyAssociation.query.\
                filter(SequenceFamilyAssociation.family.has(method_id=family_method)).\
                filter(SequenceFamilyAssociation.sequence_id.in_(sequence_ids)).all()

            seq_to_fam = {f.sequence_id: f.gene_family_id for f in family_associations}
            fam_to_data = defaultdict(list)
            famID_to_name = {}

            for f in family_associations:
                fam_to_data[f.gene_family_id].append({'id': f.sequence_id, 'name': f.sequence.name})
                famID_to_name[f.gene_family_id] = f.family.name

            for r in results_a:
                f = seq_to_fam[r.profile.sequence_id] if r.profile.sequence_id in seq_to_fam.keys() else None

                if f is None:
                    continue

                if f not in table_data.keys():
                    table_data[f] = {'id': f, 'name': famID_to_name[f], 'left_genes': [], 'right_genes': []}

                table_data[f]['left_genes'].append({'id': r.profile.sequence_id,
                                                    'name': r.profile.sequence.name,
                                                    'shortest_alias': r.profile.sequence.shortest_alias,
                                                    'low_abundance': r.profile.low_abundance})

            for r in results_b:
                f = seq_to_fam[r.profile.sequence_id] if r.profile.sequence_id in seq_to_fam.keys() else None

                if f is None:
                    continue

                if f not in table_data.keys():
                    table_data[f] = {'id': f, 'name': famID_to_name[f], 'left_genes': [], 'right_genes': []}

                table_data[f]['right_genes'].append({'id': r.profile.sequence_id,
                                                     'name': r.profile.sequence.name,
                                                     'shortest_alias': r.profile.sequence.shortest_alias,
                                                     'low_abundance': r.profile.low_abundance
                                                     })

            for f in table_data.keys():
                if len(table_data[f]['left_genes']) > 0 and len(table_data[f]['right_genes']) == 0:
                    table_data[f]['type'] = 'left'
                    counts['left'] += 1
                elif len(table_data[f]['right_genes']) > 0 and len(table_data[f]['left_genes']) == 0:
                    table_data[f]['type'] = 'right'
                    counts['right'] += 1
                else:
                    table_data[f]['type'] = 'intersection'
                    counts['intersection'] += 1

        return render_template('compare_specificity.html', counts=counts,
                               table_data=table_data,
                               labels={'left_species': species_a.name,
                                       'right_species': species_b.name,
                                       'left_method': method_a.description,
                                       'right_method': method_b.description,
                                       'left_condition': condition_a,
                                       'right_condition': condition_b},
                               use_interpro=use_interpro)