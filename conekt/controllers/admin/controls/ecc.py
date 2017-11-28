from conekt import db

from flask import flash, url_for
from conekt.extensions import admin_required
from werkzeug.utils import redirect

from conekt.controllers.admin.controls import admin_controls
from conekt.models.expression.networks import ExpressionNetworkMethod
from conekt.models.relationships.sequence_sequence_ecc import SequenceSequenceECCAssociation


@admin_controls.route('/calculate_ecc/<int:gf_method_id>')
@admin_required
def calculate_ecc(gf_method_id):
    networks = ExpressionNetworkMethod.query.all()
    network_ids = [n.id for n in networks]

    ExpressionNetworkMethod.calculate_ecc(network_ids, gf_method_id)

    flash('Successfully calculated ECC', 'success')
    return redirect(url_for('admin.ecc.index'))


@admin_controls.route('/delete_ecc/<int:gf_method_id>')
@admin_required
def delete_ecc(gf_method_id):
    SequenceSequenceECCAssociation.query.filter(SequenceSequenceECCAssociation.gene_family_method_id == gf_method_id).delete()

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(e)

    flash('Successfully deleted ECC', 'success')
    return redirect(url_for('admin.ecc.index'))
