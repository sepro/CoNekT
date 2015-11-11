import json
from statistics import mean


def prepare_profiles(profiles, normalize=False):
    """
    Function to convert a list of NetworkProfiles to a dict compatible with chart.js

    :param profiles: list of profiles to include in the plot
    :param normalize: normalize the profiles (the max value of each profile is scaled to 1)

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
            'label': p.probe if p.sequence_id is None else p.sequence.name + " (" + p.probe + ")",
            'strokeColor': 'rgba(175,175,175,0.2)',
            'pointStrokeColor': 'rgba(220,220,220,0)',
            'fillColor': 'rgba(220,220,220,0.1)',
            'pointHighlightStroke': 'rgba(220,220,220,0)',
            'pointColor': 'rgba(220,220,220,0)',
            'pointHighlightFill': 'rgba(220,220,220,0)',
            'data': expression_values
        })

    return {'labels': labels, 'datasets': datasets}
