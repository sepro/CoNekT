from flask import Blueprint, request, render_template,flash
from sqlalchemy.orm import noload

from planet import cache
from planet.models.sequences import Sequence
from planet.models.expression_profiles import ExpressionProfile
from planet.models.relationships import SequenceCoexpressionClusterAssociation
from planet.models.coexpression_clusters import CoexpressionCluster

from planet.forms.custom_network import CustomNetworkForm

from planet.helpers.chartjs import prepare_profiles

import json

custom_network = Blueprint('custom_network', __name__)


@custom_network.route('/', methods=['GET', 'POST'])
def custom_network_main():
    """
    Profile comparison tool, accepts a species and a list of probes and plots the profiles for the selected
    """
    form = CustomNetworkForm(request.form)
    form.populate_species()

    if request.method == 'POST':
        probes = request.form.get('probes').split()
        species_id = request.form.get('species_id')

        return "%s, %s" % (probes, species_id)

    else:
        return render_template("custom_network.html", form=form)
