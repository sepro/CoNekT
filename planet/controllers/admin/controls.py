from flask import Blueprint, Response, redirect, url_for, request, flash, abort
from flask_login import login_required

from planet.models.coexpression_clusters import CoexpressionClusteringMethod
from planet.models.expression_networks import ExpressionNetworkMethod, ExpressionNetwork
from planet.models.expression_profiles import ExpressionProfile
from planet.models.gene_families import GeneFamilyMethod, GeneFamily
from planet.models.species import Species
from planet.models.sequences import Sequence
from planet.models.clades import Clade
from planet.models.go import GO
from planet.models.interpro import Interpro
from planet.models.xrefs import XRef

from planet.forms.admin.add_species import AddSpeciesForm
from planet.forms.admin.add_go_interpro import AddFunctionalDataForm
from planet.forms.admin.add_go_sequences import AddGOForm
from planet.forms.admin.add_interpro_sequences import AddInterProForm
from planet.forms.admin.add_xrefs import AddXRefsForm, AddXRefsFamiliesForm
from planet.forms.admin.add_family import AddFamiliesForm
from planet.forms.admin.add_expression_profiles import AddExpressionProfilesForm
from planet.forms.admin.add_coexpression_network import AddCoexpressionNetworkForm
from planet.forms.admin.add_coexpression_clusters import AddCoexpressionClustersForm

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
        flash('An error occurred while re-doing counts', 'danger')
    else:
        flash('All count updated', 'success')

    return redirect(url_for('admin.index'))


@admin_controls.route('/update/clades')
@login_required
def update_clades():
    try:
        Clade.update_clades()
        Clade.update_clades_interpro()
    except:
        flash('An error occurred while updating clades', 'danger')
    else:
        flash('All clades updated', 'success')

    return redirect(url_for('admin.index'))


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


@admin_controls.route('/add/go', methods=['POST'])
@login_required
def add_go():
    form = AddGOForm(request.form)
    form.populate_species()

    if request.method == 'POST':
        species_id = int(request.form.get('species_id'))
        source = request.form.get('source')

        file = request.files[form.file.name].read()
        if file != b'':
            fd, temp_path = mkstemp()
            open(temp_path, 'wb').write(file)

            GO.add_go_from_tab(temp_path, species_id)

            os.close(fd)
            os.remove(temp_path)
            flash('Added GO terms from file %s' % form.file.name, 'success')
        else:
            flash('Empty file or no file provided, cannot add GO terms to sequences', 'warning')

        return redirect(url_for('admin.index'))
    else:
        if not form.validate():
            flash('Unable to validate data, potentially missing fields', 'danger')
            return redirect(url_for('admin.index'))
        else:
            abort(405)


@admin_controls.route('/add/interpro', methods=['POST'])
@login_required
def add_interpro():
    form = AddInterProForm(request.form)
    form.populate_species()

    if request.method == 'POST':
        species_id = int(request.form.get('species_id'))

        file = request.files[form.file.name].read()
        if file != b'':
            fd, temp_path = mkstemp()
            open(temp_path, 'wb').write(file)

            Interpro.add_interpro_from_interproscan(temp_path, species_id)

            os.close(fd)
            os.remove(temp_path)
            flash('Added InterPro terms from file %s' % form.file.name, 'success')
        else:
            flash('Empty file or no file provided, cannot add InterPro terms to sequences', 'warning')

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
            xref_data = request.files[form.file.name].read()
            if xref_data != b'':
                fd, temp_path = mkstemp()
                open(temp_path, 'wb').write(xref_data)

                XRef.add_xref_genes_from_file(species_id, temp_path)

                os.close(fd)
                os.remove(temp_path)
                flash('Added XRefs from file %s' % form.file.name, 'success')
            else:
                flash('Empty file or no file provided, cannot add XRefs', 'danger')

            return redirect(url_for('admin.index'))
    else:
        if not form.validate():
            flash('Unable to validate data, potentially missing fields', 'danger')
            return redirect(url_for('admin.index'))
        else:
            abort(405)


@admin_controls.route('/add/xrefs_family', methods=['POST'])
@login_required
def add_xrefs_family():
    form = AddXRefsFamiliesForm(request.form)

    if request.method == 'POST':
        gene_family_methods_id = int(request.form.get('gene_family_method_id'))

        xref_data = request.files[form.file.name].read()
        if xref_data != b'':
            fd, temp_path = mkstemp()
            open(temp_path, 'wb').write(xref_data)

            XRef.add_xref_families_from_file(gene_family_methods_id, temp_path)

            os.close(fd)
            os.remove(temp_path)
            flash('Added XRefs from file %s' % form.file.name, 'success')
        else:
            flash('Empty file or no file provided, cannot add XRefs', 'danger')

        return redirect(url_for('admin.index'))
    else:
        if not form.validate():
            flash('Unable to validate data, potentially missing fields', 'danger')
            return redirect(url_for('admin.index'))
        else:
            abort(405)


@admin_controls.route('/add/family', methods=['POST'])
@login_required
def add_family():
    form = AddFamiliesForm(request.form)

    if request.method == 'POST':
        method_description = request.form.get('method_description')
        source = request.form.get('source')

        family_data = request.files[form.file.name].read()
        if family_data != b'':
            fd, temp_path = mkstemp()
            open(temp_path, 'wb').write(family_data)

            if source == 'plaza':
                GeneFamily.add_families_from_plaza(temp_path, method_description)
                flash('Added Gene families from file %s' % form.file.name, 'success')
            else:
                flash('Method not implemented yet', 'danger')
            os.close(fd)
            os.remove(temp_path)

        else:
            flash('Empty file or no file provided, cannot add gene families', 'warning')

        return redirect(url_for('admin.index'))
    else:
        if not form.validate():
            flash('Unable to validate data, potentially missing fields', 'danger')
            return redirect(url_for('admin.index'))
        else:
            abort(405)


@admin_controls.route('/add/expression_profile', methods=['POST'])
@login_required
def add_expression_profiles():
    form = AddExpressionProfilesForm(request.form)

    if request.method == 'POST':
        species_id = int(request.form.get('species_id'))
        source = request.form.get('source')

        matrix_file = request.files[form.matrix_file.name].read()
        annotation_file = request.files[form.annotation_file.name].read()
        order_colors_file = request.files[form.order_colors_file.name].read()
        if matrix_file != b'' and annotation_file != b'':
            fd_matrix, temp_matrix_path = mkstemp()
            open(temp_matrix_path, 'wb').write(matrix_file)

            fd_annotation, temp_annotation_path = mkstemp()
            open(temp_annotation_path, 'wb').write(annotation_file)

            if order_colors_file != b'':
                fd_order_colors, temp_order_colors_path = mkstemp()
                open(temp_order_colors_path, 'wb').write(order_colors_file)

                ExpressionProfile.add_profile_from_lstrap(temp_matrix_path, temp_annotation_path, species_id,
                                                          order_color_file=temp_order_colors_path)

                os.close(fd_order_colors)
                os.remove(temp_order_colors_path)
            else:
                ExpressionProfile.add_profile_from_lstrap(temp_matrix_path, temp_annotation_path, species_id)

            os.close(fd_annotation)
            os.remove(temp_annotation_path)
            os.close(fd_matrix)
            os.remove(temp_matrix_path)

            flash('Added expression profiles for species %d' % species_id, 'success')
        else:
            flash('Empty file or no file provided, cannot add gene families', 'warning')
        return redirect(url_for('admin.index'))
    else:
        if not form.validate():
            flash('Unable to validate data, potentially missing fields', 'danger')
            return redirect(url_for('admin.index'))
        else:
            abort(405)


@admin_controls.route('/add/coexpression_network', methods=['POST'])
@login_required
def add_coexpression_network():
    form = AddCoexpressionNetworkForm(request.form)

    if request.method == 'POST':
        species_id = int(request.form.get('species_id'))
        description = request.form.get('description')
        limit = int(request.form.get('limit'))
        pcc_cutoff = float(request.form.get('pcc_cutoff'))

        file = request.files[form.file.name].read()

        if file != b'':
            fd, temp_path = mkstemp()
            open(temp_path, 'wb').write(file)

            ExpressionNetwork.read_expression_network_lstrap(temp_path, species_id, description,
                                                             pcc_cutoff=pcc_cutoff,
                                                             limit=limit)

            os.close(fd)
            os.remove(temp_path)
            flash('Added coexpression network for species %d' % species_id, 'success')
        else:
            flash('Empty or no file provided, cannot add coexpression network', 'warning')

        return redirect(url_for('admin.index'))
    else:
        if not form.validate():
            flash('Unable to validate data, potentially missing fields', 'danger')
            return redirect(url_for('admin.index'))
        else:
            abort(405)


@admin_controls.route('/add/coexpression_clusters', methods=['POST'])
@login_required
def add_coexpression_clusters():
    form = AddCoexpressionClustersForm(request.form)
    form.populate_networks()

    if request.method == 'POST' and form.validate():
        network_id = int(request.form.get('network_id'))
        description = request.form.get('description')

        file = request.files[form.file.name].read()

        if file != b'':
            fd, temp_path = mkstemp()
            open(temp_path, 'wb').write(file)

            CoexpressionClusteringMethod.add_lstrap_coexpression_clusters(temp_path, description, network_id)

            os.close(fd)
            os.remove(temp_path)
            flash('Added coexpression clusters for network method %d' % network_id, 'success')
        else:
            flash('Empty or no file provided, cannot add coexpression network', 'warning')

        return redirect(url_for('admin.index'))
    else:
        if not form.validate():
            flash('Unable to validate data, potentially missing fields', 'danger')
            return redirect(url_for('admin.index'))
        else:
            abort(405)