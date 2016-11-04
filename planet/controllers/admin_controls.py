from flask import Blueprint, current_app, Response, redirect, url_for, request, render_template, flash, abort
from flask_login import login_required
from werkzeug.utils import secure_filename

from planet.models.coexpression_clusters import CoexpressionClusteringMethod
from planet.models.expression_networks import ExpressionNetworkMethod
from planet.models.gene_families import GeneFamilyMethod
from planet.models.species import Species
from planet.models.sequences import Sequence
from planet.models.clades import Clade

from planet.forms.admin.add_species import AddSpeciesForm

import json
import os
from tempfile import mkstemp

admin_controls = Blueprint('admin_controls', __name__)


@admin_controls.route('/')
@login_required
def main():
    flash('TEST Success', 'success')

    return redirect(url_for('main.screen'))


@admin_controls.route('/update/counts')
@login_required
def update_counts():
    try:
        CoexpressionClusteringMethod.update_counts()
        ExpressionNetworkMethod.update_count()
        GeneFamilyMethod.update_count()
        Species.update_counts()
    except:
        return Response(json.dumps({'status': 'failed', 'message': 'Unable to update counts'}))
    else:
        return Response(json.dumps({'status': 'success', 'message': 'Updated all counts'}))


@admin_controls.route('/update/clades')
@login_required
def update_clades():
    try:
        Clade.update_clades()
        Clade.update_clades_interpro()
    except:
        return Response(json.dumps({'status': 'failed', 'message': 'Unable to update clades'}))
    else:
        return Response(json.dumps({'status': 'success', 'message': 'Updated all clades'}))


@admin_controls.route('/add/species', methods=['POST'])
@login_required
def add_species():
    form = AddSpeciesForm(request.form)

    if request.method == 'POST' and form.validate():
        # Add species (or return id of existing species)
        species_id = Species.add(request.form.get('code'),
                                 request.form.get('name'),
                                 data_type=request.form.get('data_type'),
                                 color=request.form.get('color'),
                                 highlight=request.form.get('highlight'))

        # Add Sequences
        fd, temp_path = mkstemp()

        fasta_data = request.files[form.fasta.name].read()

        open(temp_path, 'wb').write(fasta_data)
        Sequence.add_from_fasta(temp_path, species_id)

        os.close(fd)
        os.remove(temp_path)
        return Response("HELLO")
    else:
        if not form.validate():
            return Response(form.errors)
        else:
            abort(405)


@admin_controls.route('/add/xrefs', methods=['POST'])
@login_required
def add_xrefs():
    return Response("HELLO")


@admin_controls.route('/add/descriptions', methods=['POST'])
@login_required
def add_descriptions():
    return Response("HELLO")

