from flask import g, Blueprint, flash, redirect, url_for, render_template, request


from planet.models.interpro import Interpro

interpro = Blueprint('interpro', __name__)

@interpro.route('/')
def interpro_overview():
    return redirect(url_for('main.screen'))

@interpro.route('/view/<interpro_id>')
def interpro_view(interpro_id):
    current_interpro = Interpro.query.get_or_404(interpro_id)

    return render_template('interpro.html', interpro=current_interpro)
