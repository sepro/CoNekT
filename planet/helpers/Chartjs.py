import json
from statistics import mean


def prepare_profiles(profiles):
    """
    Function to convert a list of NetworkProfiles to a dict compatible with chart.js

    :param profiles:
    :return:
    """
    labels = []
    datasets = []

    if len(profiles) > 0:
        data = json.loads(profiles[0].profile)
        labels = data['order']

    for count, p in enumerate(profiles):
        data = json.loads(p.profile)
        datasets.append({
            'label': p.probe if p.sequence_id is None else p.sequence.name + " (" + p.probe + ")",
            'strokeColor': 'rgba(175,175,175,0.2)',
            'pointStrokeColor': 'rgba(220,220,220,0)',
            'fillColor': 'rgba(220,220,220,0.1)',
            'pointHighlightStroke': 'rgba(220,220,220,0)',
            'pointColor': 'rgba(220,220,220,0)',
            'pointHighlightFill': 'rgba(220,220,220,0)',
            'data': [mean(data['data'][label]) for label in labels]
        })

    return {'labels': labels, 'datasets': datasets}