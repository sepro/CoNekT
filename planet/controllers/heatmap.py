from flask import Blueprint, request, render_template

from planet.models.expression_profiles import ExpressionProfile
from planet.models.relationships import SequenceCoexpressionClusterAssociation
from planet.forms.heatmap import HeatmapForm

heatmap = Blueprint('heatmap', __name__)


@heatmap.route('/cluster/<cluster_id>/<species_id>')
def heatmap_cluster(cluster_id, species_id):
    associations = SequenceCoexpressionClusterAssociation.query.filter_by(coexpression_cluster_id=cluster_id).all()

    probes = [a.probe for a in associations]

    heatmap = ExpressionProfile.get_heatmap(species_id, probes)

    return render_template("expression_heatmap.html", order=heatmap['order'], profiles=heatmap['heatmap_data'])


@heatmap.route('/', methods=['GET', 'POST'])
def heatmap_main():
    form = HeatmapForm(request.form)
    form.populate_species()

    if request.method == 'POST':
        probes = request.form.get('probes').split()
        species_id = request.form.get('species_id')

        heatmap = ExpressionProfile.get_heatmap(species_id, probes)

        return render_template("expression_heatmap.html", order=heatmap['order'], profiles=heatmap['heatmap_data'], form=form)
    else:
        return render_template("expression_heatmap.html", form=form)
