from flask import Blueprint, redirect, url_for, render_template, Response

from planet.models.expression_profiles import ExpressionProfile

import json
from statistics import mean


expression_profile = Blueprint('expression_profile', __name__)


@expression_profile.route('/')
def expression_profile_overview():
    return redirect(url_for('main.screen'))

@expression_profile.route('/view/<profile_id>')
def expression_profile_view(profile_id):
    current_profile = ExpressionProfile.query.get_or_404(profile_id)

    return render_template("expression_profile.html", profile=current_profile)

@expression_profile.route('/json/<profile_id>')
def expression_profile_json(profile_id):
    current_profile = ExpressionProfile.query.get_or_404(profile_id)
    data = json.loads(current_profile.profile)

    processed_data = {}
    for key, expression_values in data.items():
        processed_data[key] = mean(expression_values)

    output = {"labels": list(processed_data.keys()),
              "datasets": [{
                    "label": "Expression Profile for " + current_profile.probe,
                    "fillColor": "rgba(220,220,220,0.2)",
                    "strokeColor": "rgba(220,220,220,1)",
                    "pointColor": "rgba(220,220,220,1)",
                    "pointStrokeColor": "#fff",
                    "pointHighlightFill": "#fff",
                    "pointHighlightStroke": "rgba(220,220,220,1)",
                    "data": list(processed_data.values())}
              ]}

    return Response(json.dumps(output), mimetype='application/json')

