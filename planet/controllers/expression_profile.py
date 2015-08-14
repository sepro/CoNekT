from flask import Blueprint, redirect, url_for, render_template, Response

from planet.models.expression_profiles import ExpressionProfile

import json
from statistics import mean


expression_profile = Blueprint('expression_profile', __name__)


@expression_profile.route('/')
def expression_profile_overview():
    """
    For lack of a better alternative redirect users to the main page
    """
    return redirect(url_for('main.screen'))

@expression_profile.route('/view/<profile_id>')
def expression_profile_view(profile_id):
    """
    Gets expression profile data from the database and renders it.

    :param profile_id: ID of the profile to show
    """
    current_profile = ExpressionProfile.query.get_or_404(profile_id)

    return render_template("expression_profile.html", profile=current_profile)


@expression_profile.route('/json/radar/<profile_id>')
def expression_profile_radar_json(profile_id):
    """
    Generates a JSON object that can be rendered using Chart.js radar plots

    :param profile_id: ID of the profile to render
    """
    current_profile = ExpressionProfile.query.get_or_404(profile_id)
    data = json.loads(current_profile.profile)

    processed_data = {}
    for key, expression_values in data["data"].items():
        processed_data[key] = mean(expression_values)

    output = {"labels": list(data["order"]),
              "datasets": [{
                    "label": "Expression Profile for " + current_profile.probe,
                    "fillColor": "rgba(220,220,220,0.2)",
                    "strokeColor": "rgba(220,220,220,1)",
                    "pointColor": "rgba(220,220,220,1)",
                    "pointStrokeColor": "#fff",
                    "pointHighlightFill": "#fff",
                    "pointHighlightStroke": "rgba(220,220,220,1)",
                    "data": list([processed_data[c] for c in data["order"]])}]}

    return Response(json.dumps(output), mimetype='application/json')


@expression_profile.route('/json/plot/<profile_id>')
def expression_profile_plot_json(profile_id):
    """
    Generates a JSON object that can be rendered using Chart.js line plots

    :param profile_id: ID of the profile to render
    """
    current_profile = ExpressionProfile.query.get_or_404(profile_id)
    data = json.loads(current_profile.profile)

    processed_means = {}
    processed_mins = {}
    processed_maxs = {}
    for key, expression_values in data["data"].items():
        processed_means[key] = mean(expression_values)
        processed_mins[key] = min(expression_values)
        processed_maxs[key] = max(expression_values)


    output = {"labels": list(data["order"]),
              "datasets": [{
                    "label": "Expression Profile for " + current_profile.probe,
                    "fillColor": "rgba(220,220,220,0.2)",
                    "strokeColor": "rgba(175,175,175,1)",
                    "pointColor": "rgba(220,220,220,1)",
                    "pointStrokeColor": "#fff",
                    "pointHighlightFill": "#fff",
                    "pointHighlightStroke": "rgba(220,220,220,1)",
                    "data": list([processed_means[c] for c in data["order"]])},
                  {
                    "label": "Minimum",
                    "fillColor": "rgba(220,220,220,0)",
                    "strokeColor": "rgba(220,22,22,0)",
                    "pointColor": "rgba(220,22,22,1)",
                    "pointStrokeColor": "#fff",
                    "pointHighlightFill": "#fff",
                    "pointHighlightStroke": "rgba(220,220,220,1)",
                    "data": list([processed_mins[c] for c in data["order"]])},
                  {
                    "label": "Maximum expression",
                    "fillColor": "rgba(220,220,220,0)",
                    "strokeColor": "rgba(220,22,22,0)",
                    "pointColor": "rgba(220,22,22,1)",
                    "pointStrokeColor": "#fff",
                    "pointHighlightFill": "#fff",
                    "pointHighlightStroke": "rgba(220,220,220,1)",
                    "data": list([processed_maxs[c] for c in data["order"]])}]}

    return Response(json.dumps(output), mimetype='application/json')
