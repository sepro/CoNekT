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


@expression_profile.route('/compare/<first_profile_id>/<second_profile_id>')
def expression_profile_compare(first_profile_id, second_profile_id):
    """
    Gets expression profile data from the database and renders it.

    :param profile_id: ID of the profile to show
    """

    return render_template("compare_profiles.html", first_profile_id=first_profile_id,
                           second_profile_id=second_profile_id)


@expression_profile.route('/find/<probe>')
def expression_profile_find(probe):
    """
    Gets expression profile data from the database and renders it.

    :param profile_id: ID of the profile to show
    """
    current_profile = ExpressionProfile.query.filter_by(probe=probe).first()

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
                    "label": "Mean",
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
                    "label": "Maximum",
                    "fillColor": "rgba(220,220,220,0)",
                    "strokeColor": "rgba(220,22,22,0)",
                    "pointColor": "rgba(220,22,22,1)",
                    "pointStrokeColor": "#fff",
                    "pointHighlightFill": "#fff",
                    "pointHighlightStroke": "rgba(220,220,220,1)",
                    "data": list([processed_maxs[c] for c in data["order"]])}]}

    return Response(json.dumps(output), mimetype='application/json')


@expression_profile.route('/json/compare_plot/<first_profile_id>/<second_profile_id>')
def expression_profile_compare_plot_json(first_profile_id, second_profile_id):
    """
    Generates a JSON object that can be rendered using Chart.js line plots

    :param profile_id: ID of the profile to render
    """
    first_profile = ExpressionProfile.query.get_or_404(first_profile_id)
    second_profile = ExpressionProfile.query.get_or_404(second_profile_id)
    data_first = json.loads(first_profile.profile)
    data_second = json.loads(second_profile.profile)

    processed_first_means = {}
    processed_second_means = {}

    for key, expression_values in data_first["data"].items():
        processed_first_means[key] = mean(expression_values)
    for key, expression_values in data_second["data"].items():
        processed_second_means[key] = mean(expression_values)

    output = {"labels": list(data_first["order"]),
              "datasets": [{
                  "label": first_profile.probe,
                  "fillColor": "rgba(220,110,110,0.2)",
                  "strokeColor": "rgba(175,87,87,1)",
                  "pointColor": "rgba(220,110,110,1)",
                  "pointStrokeColor": "#fff",
                  "pointHighlightFill": "#fff",
                  "pointHighlightStroke": "rgba(220,220,220,1)",
                  "data": list([processed_first_means[c] for c in data_first["order"]])},
                  {
                  "label": second_profile.probe,
                  "fillColor": "rgba(110,110,220,0.2)",
                  "strokeColor": "rgba(87,87,175,1)",
                  "pointColor": "rgba(110,110,220,1)",
                  "pointStrokeColor": "#fff",
                  "pointHighlightFill": "#fff",
                  "pointHighlightStroke": "rgba(220,220,220,1)",
                  "data": list([processed_second_means[c] for c in data_second["order"]])}]}

    return Response(json.dumps(output), mimetype='application/json')
