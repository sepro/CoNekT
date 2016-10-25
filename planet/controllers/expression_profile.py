from flask import Blueprint, redirect, url_for, render_template, Response
from sqlalchemy.orm import undefer

from planet import cache
from planet.models.expression_profiles import ExpressionProfile
from planet.models.condition_tissue import ConditionTissue

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
@cache.cached()
def expression_profile_view(profile_id):
    """
    Gets expression profile data from the database and renders it.

    :param profile_id: ID of the profile to show
    """
    current_profile = ExpressionProfile.query.get_or_404(profile_id)

    condition_tissue = ConditionTissue.query.filter(ConditionTissue.species_id == current_profile.species_id).all()

    tissues = []

    for ct in condition_tissue:
        tissues.append({'id': ct.id, 'name': ct.name})

    return render_template("expression_profile.html", profile=current_profile, tissues=tissues)


@expression_profile.route('/modal/<profile_id>')
@cache.cached()
def expression_profile_modal(profile_id):
    """
    Gets expression profile data from the database and renders it.

    :param profile_id: ID of the profile to show
    """
    current_profile = ExpressionProfile.query.get_or_404(profile_id)

    return render_template("modals/expression_profile.html", profile=current_profile)


@expression_profile.route('/find/<probe>')
@expression_profile.route('/find/<probe>/<species_id>')
@cache.cached()
def expression_profile_find(probe, species_id=None):
    """
    Gets expression profile data from the database and renders it.

    :param probe: Name of the probe
    :param species_id: Species ID is required to ensure a unique hit
    """
    current_profile = ExpressionProfile.query.filter_by(probe=probe)

    if species_id is not None:
        current_profile = current_profile.filter_by(species_id=species_id)

    first_profile = current_profile.first_or_404()

    return redirect(url_for('expression_profile.expression_profile_view', profile_id=first_profile.id))


@expression_profile.route('/compare/<first_profile_id>/<second_profile_id>')
@expression_profile.route('/compare/<first_profile_id>/<second_profile_id>/<int:normalize>')
@cache.cached()
def expression_profile_compare(first_profile_id, second_profile_id, normalize=0):
    """
    Gets expression profile data from the database and renders it.

    :param first_profile_id: internal ID of the first profile
    :param second_profile_id: internal ID of the second profile
    :param normalize: 1 to normalize profiles (to max value), 0 to disable
    :return:
    """
    first_profile = ExpressionProfile.query.get_or_404(first_profile_id)
    second_profile = ExpressionProfile.query.get_or_404(second_profile_id)

    return render_template("compare_profiles.html",
                           first_profile=first_profile,
                           second_profile=second_profile,
                           normalize=normalize)


@expression_profile.route('/compare_probes/<probe_a>/<probe_b>/<int:species_id>')
@expression_profile.route('/compare_probes/<probe_a>/<probe_b>/<int:species_id>/<int:normalize>')
@cache.cached()
def expression_profile_compare_probes(probe_a, probe_b, species_id, normalize=0):
    """
    Gets expression profile data from the database and renders it.

    :param probe_a: name of the first probe
    :param probe_b: name of the second probe
    :param species_id: internal id of the species the probes are linked with
    :param normalize: 1 to normalize profiles (to max value), 0 to disable
    :return:
    """
    first_profile = ExpressionProfile.query.filter_by(probe=probe_a).filter_by(species_id=species_id).first_or_404()
    second_profile = ExpressionProfile.query.filter_by(probe=probe_b).filter_by(species_id=species_id).first_or_404()

    return render_template("compare_profiles.html",
                           probe_a=probe_a,
                           probe_b=probe_b,
                           first_profile=first_profile,
                           second_profile=second_profile,
                           species_id=species_id,
                           normalize=normalize)


@expression_profile.route('/json/plot/<profile_id>')
@cache.cached()
def expression_profile_plot_json(profile_id):
    """
    Generates a JSON object that can be rendered using Chart.js line plots

    :param profile_id: ID of the profile to render
    """
    current_profile = ExpressionProfile.query.options(undefer('profile')).get_or_404(profile_id)
    data = json.loads(current_profile.profile)

    processed_means = {}
    processed_mins = {}
    processed_maxs = {}

    for key, expression_values in data["data"].items():
        processed_means[key] = mean(expression_values)
        processed_mins[key] = min(expression_values)
        processed_maxs[key] = max(expression_values)

    background_color = data["colors"] if "colors" in data.keys() else "rgba(175,175,175,0.2)"
    point_color = "rgba(55,55,55,0.8)" if "colors" in data.keys() else "rgba(220,22,22,1)"

    output = {"type": "bar",
              "data": {
                      "labels": list(data["order"]),
                      "datasets": [
                          {
                            "type": "line",
                            "label": "Minimum",
                            "fill": False,
                            "showLine": False,
                            "pointBorderColor": point_color,
                            "pointBackgroundColor": point_color,
                            "data": list([processed_mins[c] for c in data["order"]])},
                          {
                            "type": "line",
                            "label": "Maximum",
                            "fill": False,
                            "showLine": False,
                            "pointBorderColor": point_color,
                            "pointBackgroundColor": point_color,
                            "data": list([processed_maxs[c] for c in data["order"]])},
                          {
                            "label": "Mean",
                            "backgroundColor": background_color,
                            "data": list([processed_means[c] for c in data["order"]])}]
                      },
              "options": {
                  "legend": {
                    "display": False
                  },
                  "scales": {
                      "xAxes": [{
                        "gridLines": {
                            "display": False
                        },
                        "ticks": {
                            "maxRotation": 90,
                            "minRotation": 90
                        }
                      }
                      ],
                      "yAxes": [{
                        "ticks": {
                            "beginAtZero": True
                        }
                      }
                      ]
                  }
              }
              }

    return Response(json.dumps(output), mimetype='application/json')


@expression_profile.route('/json/plot/<profile_id>/<condition_tissue_id>')
@cache.cached()
def expression_profile_plot_tissue_json(profile_id, condition_tissue_id):
    """
    Generates a JSON object that can be rendered using Chart.js line plots

    :param profile_id: ID of the profile to render
    :param condition_tissue_id: ID of the condition to tissue conversion to be used
    """
    current_profile = ExpressionProfile.query.options(undefer('profile')).get_or_404(profile_id)
    data = current_profile.tissue_profile(condition_tissue_id)

    processed_means = {}
    processed_maxs = {}
    processed_mins = {}

    for key, expression_values in data["data"].items():
        processed_means[key] = mean(expression_values)

        processed_maxs[key] = max(expression_values)
        processed_mins[key] = min(expression_values)

    output = {"type": "bar",
              "data": {
                  "labels": list(data["order"]),
                  "datasets": [{"type": "line",
                                "label": "Maximum",
                                "fill": False,
                                "showLine": False,
                                "pointBorderColor": "rgba(220,22,22,1)",
                                "pointBackgroundColor": "rgba(220,22,22,1)",
                                "data": list([processed_maxs[c] for c in data["order"]])},
                               {
                                "type": "line",
                                "label": "Minimum",
                                "fill": False,
                                "showLine": False,
                                "pointBorderColor": "rgba(220,22,22,1)",
                                "pointBackgroundColor": "rgba(220,22,22,1)",
                                "data": list([processed_mins[c] for c in data["order"]])},
                               {
                                "label": "Mean",
                                "backgroundColor": "rgba(175,175,175,0.2)",
                                "data": list([processed_means[c] for c in data["order"]])}]
                  },
              "options": {
                  "legend": {
                    "display": False
                  },
                  "scales": {
                      "xAxes": [{
                        "gridLines": {
                            "display": False
                        },
                        "ticks": {
                            "maxRotation": 90,
                            "minRotation": 90
                        }
                      }
                      ],
                      "yAxes": [{
                        "ticks": {
                            "beginAtZero": True
                        }
                      }
                      ]
                  }
              }
              }

    return Response(json.dumps(output), mimetype='application/json')


@expression_profile.route('/json/compare_plot/<first_profile_id>/<second_profile_id>')
@expression_profile.route('/json/compare_plot/<first_profile_id>/<second_profile_id>/<int:normalize>')
@cache.cached()
def expression_profile_compare_plot_json(first_profile_id, second_profile_id, normalize=0):
    """
    Generates a JSON object with two profiles that can be rendered using Chart.js line plots

    :param profile_id: ID of the profile to render
    """
    first_profile = ExpressionProfile.query.options(undefer('profile')).get_or_404(first_profile_id)
    second_profile = ExpressionProfile.query.options(undefer('profile')).get_or_404(second_profile_id)
    data_first = json.loads(first_profile.profile)
    data_second = json.loads(second_profile.profile)

    processed_first_means = {}
    processed_second_means = {}

    for key, expression_values in data_first["data"].items():
        processed_first_means[key] = mean(expression_values)
    for key, expression_values in data_second["data"].items():
        processed_second_means[key] = mean(expression_values)

    first_max = max([v for _, v in processed_first_means.items()])
    second_max = max([v for _, v in processed_second_means.items()])

    if normalize == 1:
        for k, v in processed_first_means.items():
            processed_first_means[k] = v/first_max

        for k, v in processed_second_means.items():
            processed_second_means[k] = v/second_max

    output = {"type": "bar",
              "data": {
                          "labels": list(data_first["order"]),
                          "datasets": [{
                              "label": first_profile.probe,
                              "backgroundColor": "rgba(220,22,22,0.5)",
                              "data": list([processed_first_means[c] for c in data_first["order"]])},
                              {
                              "label": second_profile.probe,
                              "backgroundColor": "rgba(22,22,220,0.5)",
                              "data": list([processed_second_means[c] for c in data_second["order"]])}]
              },
              "options": {
                  "legend": {
                    "display": True
                  },
                  "scales": {
                      "xAxes": [{
                        "gridLines": {
                            "display": False
                        },
                        "ticks": {
                            "maxRotation": 90,
                            "minRotation": 90
                        }
                      }
                      ],
                      "yAxes": [{
                        "ticks": {
                            "beginAtZero": True
                        }
                      }
                      ]
                  }
              }
              }

    return Response(json.dumps(output), mimetype='application/json')
