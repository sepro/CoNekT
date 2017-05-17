from flask import flash, url_for
from flask_login import login_required
from werkzeug.utils import redirect

from planet.controllers.admin.controls import admin_controls
from planet.models.expression.networks import ExpressionNetworkMethod


@admin_controls.route('/calculate_ecc/<int:gf_method_id>')
@login_required
def calculate_ecc(gf_method_id):
    networks = ExpressionNetworkMethod.query.all()
    network_ids = [n.id for n in networks]

    ExpressionNetworkMethod.calculate_ecc(network_ids, gf_method_id)

    flash('Successfully calculated ECC', 'success')
    return redirect(url_for('admin.controls.index'))