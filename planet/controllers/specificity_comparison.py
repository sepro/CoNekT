from flask import Blueprint, request, render_template,flash
from sqlalchemy.orm import noload

from planet import cache
from planet.models.sequences import Sequence
from planet.models.expression_profiles import ExpressionProfile
from planet.models.relationships import SequenceCoexpressionClusterAssociation
from planet.models.coexpression_clusters import CoexpressionCluster

from planet.forms.compare_specificity import CompareSpecificityForm

from planet.helpers.chartjs import prepare_profiles

import json

specificity_comparison = Blueprint('specificity_comparison', __name__)


@specificity_comparison.route('/', methods=['GET', 'POST'])
def specificity_comparison_main():
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

        return '...'.join([species_a_id, species_b_id, method_a_id, method_b_id, condition_a, condition_b, cutoff_a, cutoff_b])