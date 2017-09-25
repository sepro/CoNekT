import json
from statistics import mean

from utils.color import __COLORS_RGBA as COLORS


def prepare_profiles_download(profiles, normalize=False):
    """
    Function to convert a list of NetworkProfiles to a dict compatible with chart.js

    :param profiles: list of profiles to include in the plot
    :param normalize: normalize the profiles (the max value of each profile is scaled to 1)

    :return dict with plot compatible with Chart.js
    """
    labels = []

    if len(profiles) > 0:
        data = json.loads(profiles[0].profile)
        labels = data['order']

    # initiate output array with header
    output = ['genes\t' + '\t'.join(labels)]

    for count, p in enumerate(profiles):
        data = json.loads(p.profile)
        expression_values = [mean(data['data'][label]) for label in labels]
        label = p.probe if p.sequence_id is None else p.sequence.name

        if normalize:
            max_expression = max(expression_values)
            expression_values = [value/max_expression for value in expression_values]

        output.append(label + '\t' + '\t'.join(str(e) for e in expression_values))

    return '\n'.join(output)


def prepare_profiles(profiles, normalize=False, xlabel='', ylabel=''):
    """
    Function to convert a list of NetworkProfiles to a dict compatible with chart.js

    :param profiles: list of profiles to include in the plot
    :param normalize: normalize the profiles (the max value of each profile is scaled to 1)
    :param xlabel: label for x-axis
    :param ylabel: label for y-axis

    :return dict with plot compatible with Chart.js
    """
    labels = []
    datasets = []

    if len(profiles) > 0:
        data = json.loads(profiles[0].profile)
        labels = data['order']

    for count, p in enumerate(profiles):
        data = json.loads(p.profile)
        expression_values = [mean(data['data'][label]) for label in labels]

        if normalize:
            max_expression = max(expression_values)
            expression_values = [value/max_expression for value in expression_values]

        datasets.append({
            'label': p.probe if p.sequence_id is None else p.sequence.name,
            'fill': True,
            'showLine': True,
            'backgroundColor': "rgba(220,220,220,0.1)" if len(profiles) >= 10 else COLORS[count],
            'borderColor': "rgba(175,175,175,0.2)" if len(profiles) >= 10 else COLORS[count],
            'pointRadius': 5 if len(profiles) < 10 else 0,
            'data': expression_values
        })

    output = {
        'type': 'line',
        'data': {
            'labels': labels,
            'datasets': datasets
        },
        "options": {
          "legend": {
            "display": len(profiles) < 10
          },
          "tooltips": {
            "enabled": len(profiles) < 10,
            "mode": 'label',
            "intersect": True
          },
          "scales": {
              "xAxes": [{
                  "scaleLabel": {
                      "display": xlabel != '',
                      "labelString": xlabel
                  },
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
                "scaleLabel": {
                    "display": ylabel != '',
                    "labelString": ylabel
                },
                "ticks": {
                    "beginAtZero": True
                }
              }
              ]
          }
        }
    }

    return output


def prepare_expression_profile(data, show_sample_count=False, xlabel='', ylabel=''):
    """
    Converts data from Expression Profile to a format compatible with Chart.js

    :param data: dat from Expression Profile model
    :param show_sample_count: includes the number of samples in the plot
    :param xlabel: label for x-axis
    :param ylabel: label for y-axis
    :return: dict compatible with Chart.js
    """
    processed_means = {}
    processed_mins = {}
    processed_maxs = {}
    counts = {}

    for key, expression_values in data["data"].items():
        processed_means[key] = mean(expression_values)
        processed_mins[key] = min(expression_values)
        processed_maxs[key] = max(expression_values)
        counts[key] = len(expression_values)

    background_color = data["colors"] if "colors" in data.keys() else "rgba(175,175,175,0.2)"
    point_color = "rgba(55,55,55,0.8)" if "colors" in data.keys() else "rgba(220,22,22,1)"

    output = {"type": "bar",
              "data": {
                      "labels": list(data["order"]),
                      "counts": list([counts[c] for c in data["order"]]) if show_sample_count else [None]*len(data["order"]),
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
                        "scaleLabel": {
                              "display": xlabel != '',
                              "labelString": xlabel
                          },
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
                          "scaleLabel": {
                              "display": ylabel != '',
                              "labelString": ylabel
                          },
                          "ticks": {
                            "beginAtZero": True
                        }
                      }
                      ]
                  }
              }
              }

    return output


def prepare_profile_comparison(data_first, data_second, labels, normalize=1, xlabel='', ylabel=''):
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
                              "label": labels[0],
                              "backgroundColor": "rgba(220,22,22,0.5)",
                              "data": list([processed_first_means[c] for c in data_first["order"]])},
                              {
                              "label": labels[1],
                              "backgroundColor": "rgba(22,22,220,0.5)",
                              "data": list([processed_second_means[c] for c in data_second["order"]])}]
              },
              "options": {
                  "legend": {
                    "display": True
                  },
                  "scales": {
                      "xAxes": [{
                        "scaleLabel": {
                              "display": xlabel != '',
                              "labelString": xlabel
                        },
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
                        "scaleLabel": {
                            "display": ylabel != '',
                            "labelString": ylabel
                        },
                        "ticks": {
                            "beginAtZero": True
                        }
                      }
                      ]
                  }
              }
              }

    return output


def prepare_doughnut(counts):
    output = {
        "data": {
            "labels": [counts[s]["label"] for s in counts.keys()],
            "datasets": [{
                "data": [counts[s]["value"] for s in counts.keys()],
                "backgroundColor": [counts[s]["color"] for s in counts.keys()],
                "hoverBackgroundColor": [counts[s]["color"] for s in counts.keys()]
            }]
        }
        ,
        "type": "doughnut"
    }

    return output
