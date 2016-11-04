from flask import Blueprint, current_app, Response, redirect, url_for, request, render_template, flash, abort
from flask_login import login_required
from werkzeug.utils import secure_filename

from planet.models.coexpression_clusters import CoexpressionClusteringMethod
from planet.models.expression_networks import ExpressionNetworkMethod
from planet.models.gene_families import GeneFamilyMethod
from planet.models.species import Species
from planet.models.sequences import Sequence
from planet.models.clades import Clade
from planet.models.go import GO
from planet.models.interpro import Interpro
from planet.models.xrefs import XRef

from planet.forms.admin.add_species import AddSpeciesForm
from planet.forms.admin.add_go_interpro import AddFunctionalDataForm
from planet.forms.admin.add_xrefs import AddXRefsForm


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

        print(request.files[form.fasta.name].content_type)

        compressed = 'gzip' in request.files[form.fasta.name].content_type

        open(temp_path, 'wb').write(fasta_data)
        sequence_count = Sequence.add_from_fasta(temp_path, species_id, compressed=compressed)

        os.close(fd)
        os.remove(temp_path)
        flash('Addes species %s and %d sequences' % (request.form.get('name'), sequence_count), 'success')
        return redirect(url_for('admin.index'))
    else:
        if not form.validate():
            flash('Unable to validate data, potentially missing fields', 'danger')
            return redirect(url_for('admin.index'))
        else:
            abort(405)


@admin_controls.route('/add/descriptions', methods=['POST'])
@login_required
def add_descriptions():
    return Response("HELLO")


@admin_controls.route('/add/functional_data', methods=['POST'])
@login_required
def add_functional_data():
    form = AddFunctionalDataForm(request.form)

    if request.method == 'POST' and form.validate():
        # Add GO
        go_data = request.files[form.go.name].read()
        go_compressed = 'gzip' in request.files[form.go.name].content_type
        if go_data != b'':
            fd, temp_path = mkstemp()
            open(temp_path, 'wb').write(go_data)
            GO.add_from_obo(temp_path, empty=True,compressed=go_compressed)

            os.close(fd)
            os.remove(temp_path)
            flash('GO data added.', 'success')
        else:
            flash('No GO data selected, skipping ...', 'warning')

        # Add InterPro
        interpro_data = request.files[form.interpro.name].read()
        if interpro_data != b'':
            fd, temp_path = mkstemp()
            open(temp_path, 'wb').write(interpro_data)
            Interpro.add_from_xml(temp_path, empty=True)

            os.close(fd)
            os.remove(temp_path)
            flash('InterPro data added.', 'success')
        else:
            flash('No InterPro data selected, skipping ...', 'warning')
        return redirect(url_for('admin.index'))
    else:
        if not form.validate():
            flash('Unable to validate data, potentially missing fields', 'danger')
            return redirect(url_for('admin.index'))
        else:
            abort(405)


@admin_controls.route('/add/xrefs', methods=['POST'])
@login_required
def add_xrefs():
    form = AddXRefsForm(request.form)

    if request.method == 'POST':
        species_id = int(request.form.get('species_id'))
        platform = request.form.get('platforms')

        if platform == 'plaza_3_dicots':
            XRef.create_plaza_xref_genes(species_id)
            flash('Added XRefs to PLAZA 3.0 dicots for species id %d' % species_id, 'success')
            return redirect(url_for('admin.index'))
        elif platform == 'evex':
            XRef.create_evex_xref_genes(species_id)
            flash('Added XRefs to EVEX dicots for species id %d' % species_id, 'success')
            return redirect(url_for('admin.index'))
        else:
            flash('This platform is not implemented, nothing added/changed/deleted from the database', 'warning')
            return redirect(url_for('admin.index'))
    else:
        if not form.validate():
            flash('Unable to validate data, potentially missing fields', 'danger')
            return redirect(url_for('admin.index'))
        else:
            abort(405)

