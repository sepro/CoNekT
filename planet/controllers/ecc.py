from flask import Blueprint, redirect, url_for
from sqlalchemy import and_

from planet.models.sequences import Sequence
from planet.models.relationships import SequenceSequenceECCAssociation

import json

ecc = Blueprint('ecc', __name__)


@ecc.route('/')
def ecc_overview():
    """
    For lack of a better alternative redirect users to the main page
    """
    return redirect(url_for('main.screen'))


@ecc.route('/json/<int:sequence>/<int:network>/<int:family>')
def ecc_graph_json(sequence, network, family):

    sequence = Sequence.query.get_or_404(sequence)
    data = sequence.ecc_query_associations.filter(and_(
            SequenceSequenceECCAssociation.query_network_method_id == network,
            SequenceSequenceECCAssociation.gene_family_method_id == family)).all()

    output = []

    for d in data:
        output.append({
            'query': d.query_id,
            'target': d.target_id
        })

    return json.dumps(output)
