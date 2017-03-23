import json
import os
from tempfile import mkstemp

from flask import Blueprint, Markup, redirect, url_for, request, flash, abort, current_app
from flask_login import login_required

from planet import cache, whooshee
from planet.forms.admin.add_clades import AddCladesForm
from planet.forms.admin.add_coexpression_clusters import AddCoexpressionClustersForm
from planet.forms.admin.build_coexpression_clusters import BuildCoexpressionClustersForm
from planet.forms.admin.neighborhood_to_clusters import NeighborhoodToClustersForm
from planet.forms.admin.add_coexpression_network import AddCoexpressionNetworkForm
from planet.forms.admin.add_expression_profiles import AddExpressionProfilesForm
from planet.forms.admin.add_expression_specificity import AddTissueSpecificityForm, AddConditionSpecificityForm
from planet.forms.admin.add_family import AddFamiliesForm
from planet.forms.admin.add_go_interpro import AddFunctionalDataForm
from planet.forms.admin.add_go_sequences import AddGOForm
from planet.forms.admin.add_interpro_sequences import AddInterProForm
from planet.forms.admin.add_species import AddSpeciesForm
from planet.forms.admin.add_xrefs import AddXRefsForm, AddXRefsFamiliesForm
from planet.forms.admin.add_sequence_descriptions import AddSequenceDescriptionsForm

from planet.ftp import export_coding_sequences, export_families, export_protein_sequences, export_go_annotation, \
    export_interpro_annotation, export_coexpression_clusters, export_expression_networks

from planet.models.blast_db import BlastDB
from planet.models.clades import Clade
from planet.models.condition_tissue import ConditionTissue
from planet.models.expression.coexpression_clusters import CoexpressionCluster
from planet.models.expression.coexpression_clusters import CoexpressionClusteringMethod
from planet.models.expression.networks import ExpressionNetworkMethod, ExpressionNetwork
from planet.models.expression.profiles import ExpressionProfile
from planet.models.expression.specificity import ExpressionSpecificityMethod
from planet.models.gene_families import GeneFamilyMethod, GeneFamily
from planet.models.go import GO
from planet.models.interpro import Interpro
from planet.models.sequences import Sequence
from planet.models.species import Species
from planet.models.xrefs import XRef
from planet.models.relationships.cluster_similarity import CoexpressionClusterSimilarity

admin_controls = Blueprint('admin_controls', __name__)


@admin_controls.route('/update/counts')
@login_required
def update_counts():
    """
    Controller that will update pre-computed counts in the database.

    :return: Redirect to admin panel interface
    """
    try:
        CoexpressionClusteringMethod.update_counts()
    except Exception as e:
        print("ERROR:", e)
        flash('An error occurred while re-doing CoexpressionClusteringMethod counts', 'danger')
    else:
        flash('CoexpressionClusteringMethod count updated', 'success')

    try:
        ExpressionNetworkMethod.update_count()
    except Exception as e:
        print("ERROR:", e)
        flash('An error occurred while re-doing ExpressionNetworkMethod counts', 'danger')
    else:
        flash('ExpressionNetworkMethod counts updated', 'success')

    try:
        GeneFamilyMethod.update_count()
    except Exception as e:
        print("ERROR:", e)
        flash('An error occurred while re-doing GeneFamilyMethod counts', 'danger')
    else:
        flash('GeneFamilyMethod count updated', 'success')

    try:
        Species.update_counts()
    except Exception as e:
        print("ERROR:", e)
        flash('An error occurred while re-doing Species counts', 'danger')
    else:
        flash('Species count updated', 'success')

    try:
        GO.update_species_counts()
    except Exception as e:
        print("ERROR:", e)
        flash('An error occurred while re-doing GO counts', 'danger')
    else:
        flash('GO count updated', 'success')

    return redirect(url_for('admin.index'))


@admin_controls.route('/update/clades')
@login_required
def update_clades():
    """
    Controller that will update the clade information for gene families and interpro domains. It will detect in which
    clade a family/domain originated and add that info to the database.

    :return: Redirect to admin panel interface
    """
    try:
        Clade.update_clades()
        Clade.update_clades_interpro()
    except Exception as e:
        flash('An error occurred while updating clades', 'danger')
    else:
        flash('All clades updated', 'success')

    return redirect(url_for('admin.index'))


@admin_controls.route('/reindex/whooshee')
@login_required
def reindex_whooshee():
    """
    Touching this endpoint reindex Whooshee

    :return: Redirect to admin controls
    """
    try:
        whooshee.reindex()
    except Exception as e:
        flash('An error occurred while reindexing whooshee', 'danger')
    else:
        flash('Whooshee index rebuilt', 'success')

    return redirect(url_for('admin.controls.index'))


@admin_controls.route('/clear/cache')
@login_required
def clear_cache():
    """
    Touching this endpoint will clear the servers cache (all of it!).

    :return: Redirect to admin controls
    """
    try:
        cache.clear()
    except Exception as e:
        flash('An error occurred while clearing the cache', 'danger')
    else:
        flash('Cache cleared', 'success')

    return redirect(url_for('admin.controls.index'))


@admin_controls.route('/build_blast_db')
@login_required
def build_blast_db():
    """
    Touching this endpoint will export cds and protein fasta files and build a database using those files. Paths
    and commands specified in the config file are used.

    :return: Redirect to admin controls
    """
    try:
        BlastDB.create_db()
    except Exception as e:
        flash('An error occurred while building the Blast DB', 'danger')
    else:
        flash('Blast DB build', 'success')

    return redirect(url_for('admin.controls.index'))


@admin_controls.route('/add/species', methods=['POST'])
@login_required
def add_species():
    """
    Adds a species to the species table and adds sequences for that species to the sequence table based on the fasta
    file provided.

    :return: Redirect to admin panel interface
    """
    form = AddSpeciesForm(request.form)

    if request.method == 'POST' and form.validate():
        # Add species (or return id of existing species)
        species_id = Species.add(request.form.get('code'),
                                 request.form.get('name'),
                                 data_type=request.form.get('data_type'),
                                 color='#' + request.form.get('color'),
                                 highlight='#' + request.form.get('highlight'),
                                 description=request.form.get('description'))

        # Add Sequences
        fd, temp_path = mkstemp()

        fasta_data = request.files[form.fasta.name].read()

        print(request.files[form.fasta.name].content_type)

        compressed = 'gzip' in request.files[form.fasta.name].content_type

        with open(temp_path, 'wb') as fasta_writer:
            fasta_writer.write(fasta_data)
        sequence_count = Sequence.add_from_fasta(temp_path, species_id, compressed=compressed)

        os.close(fd)
        os.remove(temp_path)
        flash('Added species %s with %d sequences' % (request.form.get('name'), sequence_count), 'success')
        return redirect(url_for('admin.index'))
    else:
        if not form.validate():
            flash('Unable to validate data, potentially missing fields', 'danger')
            return redirect(url_for('admin.index'))
        else:
            abort(405)


@admin_controls.route('/add/sequence_descriptions', methods=['POST'])
@login_required
def add_descriptions():
    form = AddSequenceDescriptionsForm(request.form)

    if request.method == 'POST':
        species_id = int(request.form.get('species_id'))

        description_data = request.files[form.file.name].read()
        if description_data != b'':
            fd, temp_path = mkstemp()

            with open(temp_path, 'wb') as desc_writer:
                desc_writer.write(description_data)

            Sequence.add_descriptions(temp_path, species_id)

            os.close(fd)
            os.remove(temp_path)
            flash('Added descriptions from file %s' % form.file.name, 'success')
        else:
            flash('Empty file or no file provided, cannot add descriptions', 'danger')

        return redirect(url_for('admin.index'))
    else:
        if not form.validate():
            flash('Unable to validate data, potentially missing fields', 'danger')
            return redirect(url_for('admin.index'))
        else:
            abort(405)


@admin_controls.route('/add/functional_data', methods=['POST'])
@login_required
def add_functional_data():
    """
    Controller to populate the GO structure and descriptions and InterPro domains with descriptions to the corresponding
    tables.

    Will empty the tables prior to uploading the new information, this might break links with existing GO terms assigned
    to sequences !

    :return: Redirect to admin panel interface
    """
    form = AddFunctionalDataForm(request.form)

    if request.method == 'POST' and form.validate():
        # Add GO
        go_data = request.files[form.go.name].read()
        go_compressed = 'gzip' in request.files[form.go.name].content_type
        if go_data != b'':
            fd, temp_path = mkstemp()

            with open(temp_path, 'wb') as go_writer:
                go_writer.write(go_data)

            GO.add_from_obo(temp_path, empty=True, compressed=go_compressed)

            os.close(fd)
            os.remove(temp_path)
            flash('GO data added.', 'success')
        else:
            flash('No GO data selected, skipping ...', 'warning')

        # Add InterPro
        interpro_data = request.files[form.interpro.name].read()
        if interpro_data != b'':
            fd, temp_path = mkstemp()

            with open(temp_path, 'wb') as interpro_writer:
                interpro_writer.write(interpro_data)

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
    """
    Adds GO labels to sequences using a tab-delimited text-file

    On relation per line like this:

    sequence_name   GO_term evidence_code
    ...

    :return: Redirect to admin panel interface
    """
    form = AddGOForm(request.form)
    form.populate_species()

    if request.method == 'POST':
        species_id = int(request.form.get('species_id'))
        source = request.form.get('source')

        file = request.files[form.file.name].read()
        if file != b'':
            fd, temp_path = mkstemp()

            with open(temp_path, 'wb') as go_writer:
                go_writer.write(file)

            GO.add_go_from_tab(temp_path, species_id, source=source)

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
    """
    Adds InterPro domain information to sequences based on InterProScan output

    :return: Redirect to admin panel interface
    """
    form = AddInterProForm(request.form)
    form.populate_species()

    if request.method == 'POST':
        species_id = int(request.form.get('species_id'))

        file = request.files[form.file.name].read()
        if file != b'':
            fd, temp_path = mkstemp()
            with open(temp_path, 'wb') as interpro_writer:
                interpro_writer.write(file)

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
    """
    Adds external references to sequences. A few platforms are included by default (note that this only works if the
    sequence name is the same in PlaNet and the third-party platform)

    A tab-delimited text-file can be uploaded with the following structure:

    sequence_name(planet)   sequence_name(other platform)   platform_name   url
    ...

    :return: Redirect to admin panel interface
    """
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

                with open(temp_path, 'wb') as xref_writer:
                    xref_writer.write(xref_data)

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
    """
    Adds external references to gene families. A tab-delimited text-file can be uploaded with the following structure:

    family_name(planet)   family_name(other platform)   platform_name   url
    ...

    :return: Redirect to admin panel interface
    """
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
    """
    Add gene families to PlaNet from various sources.

    :return: Redirect to admin panel interface:
    """
    form = AddFamiliesForm(request.form)

    if request.method == 'POST':
        method_description = request.form.get('method_description')
        source = request.form.get('source')

        family_data = request.files[form.file.name].read()
        if family_data != b'':
            fd, temp_path = mkstemp()

            with open(temp_path, 'wb') as family_writer:
                family_writer.write(family_data)

            if source == 'mcl':
                GeneFamily.add_families_from_mcl(temp_path, method_description)
                flash('Added Gene families from file %s' % form.file.name, 'success')
            elif source == 'orthofinder':
                GeneFamily.add_families_from_orthofinder(temp_path, method_description)
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
    """
    Add expression profiles to sequences based on data from LSTrAP

    :return: Redirect to admin panel interface
    """
    form = AddExpressionProfilesForm(request.form)

    if request.method == 'POST':
        species_id = int(request.form.get('species_id'))
        source = request.form.get('source')

        matrix_file = request.files[form.matrix_file.name].read()
        annotation_file = request.files[form.annotation_file.name].read()
        order_colors_file = request.files[form.order_colors_file.name].read()
        if matrix_file != b'' and annotation_file != b'':
            fd_matrix, temp_matrix_path = mkstemp()

            with open(temp_matrix_path, 'wb') as matrix_writer:
                matrix_writer.write(matrix_file)

            fd_annotation, temp_annotation_path = mkstemp()
            with open(temp_annotation_path, 'wb') as annotation_writer:
                annotation_writer.write(annotation_file)

            if order_colors_file != b'':
                fd_order_colors, temp_order_colors_path = mkstemp()
                with open(temp_order_colors_path, 'wb') as oc_writer:
                    oc_writer.write(order_colors_file)

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
    """
    Adds the co-expression network for a species based on LSTrAP output

    :return: Redirect to admin panel interface
    """
    form = AddCoexpressionNetworkForm(request.form)

    if request.method == 'POST':
        species_id = int(request.form.get('species_id'))
        description = request.form.get('description')
        limit = int(request.form.get('limit'))
        pcc_cutoff = float(request.form.get('pcc_cutoff'))

        file = request.files[form.file.name].read()

        if file != b'':
            fd, temp_path = mkstemp()
            with open(temp_path, 'wb') as network_writer:
                network_writer.write(file)

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


@admin_controls.route('/build/neighborhoods_to_clusters', methods=['POST'])
@login_required
def neighborhoods_to_clusters():
    form = NeighborhoodToClustersForm(request.form)
    form.populate_networks()
    if request.method == 'POST' and form.validate():
        network_method_id = int(request.form.get('network_id'))
        description = request.form.get('description')
        CoexpressionClusteringMethod.clusters_from_neighborhoods(description, network_method_id)

        flash('Succesfully build clusters from neighborhoods.', 'success')
        return redirect(url_for('admin.index'))
    else:
        if not form.validate():
            flash('Unable to validate data, potentially missing fields', 'danger')
            return redirect(url_for('admin.index'))
        else:
            abort(405)


@admin_controls.route('/build/hcca_clusters', methods=['POST'])
@login_required
def build_hcca_clusters():
    """
    Controller that will start building HCCA clusters for a selected network

    :return: return to admin index
    """
    form = BuildCoexpressionClustersForm(request.form)
    form.populate_networks()
    if request.method == 'POST' and form.validate():
        network_method_id = int(request.form.get('network_id'))
        description = request.form.get('description')
        CoexpressionClusteringMethod.build_hcca_clusters(description, network_method_id)

        flash('Succesfully build clusters using HCCA.', 'success')
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
    """
    Add co-expression clusters, based on LSTrAP output (MCL clusters)

    :return: Redirect to admin panel interface
    """
    form = AddCoexpressionClustersForm(request.form)
    form.populate_networks()

    if request.method == 'POST' and form.validate():
        network_id = int(request.form.get('network_id'))
        description = request.form.get('description')
        min_size = int(request.form.get('min_size'))

        file = request.files[form.file.name].read()

        if file != b'':
            fd, temp_path = mkstemp()

            with open(temp_path, 'wb') as cluster_writer:
                cluster_writer.write(file)

            CoexpressionClusteringMethod.add_lstrap_coexpression_clusters(temp_path, description, network_id,
                                                                          min_size=min_size)

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


@admin_controls.route('/add/clades', methods=['POST'])
@login_required
def add_clades():
    """
    Adds clades to the database based on a structured JSON object.

    :return: Redirect to admin panel interface
    """
    form = AddCladesForm(request.form)

    if request.method == 'POST' and form.validate():
        clades_json = json.loads(request.form.get('clades_json'))

        Clade.add_clades_from_json(clades_json)

        flash('Added clades %s to the database' % ', '.join(clades_json.keys()), 'success')
        return redirect(url_for('admin.index'))
    else:
        if not form.validate():
            flash('Unable to validate data, potentially missing fields', 'danger')
            return redirect(url_for('admin.index'))
        else:
            abort(405)


@admin_controls.route('/add/condition_specificity', methods=['POST'])
@login_required
def add_condition_specificity():
    form = AddConditionSpecificityForm(request.form)
    form.populate_species()

    if request.method == 'POST' and form.validate():
        species_id = int(request.form.get('species_id'))
        description = request.form.get('description')

        ExpressionSpecificityMethod.calculate_specificities(species_id, description, False)

        flash('Calculated condition specificities for species %d' % species_id, 'success')
        return redirect(url_for('admin.index'))
    else:
        if not form.validate():
            flash('Unable to validate data, potentially missing fields', 'danger')
            return redirect(url_for('admin.index'))
        else:
            abort(405)


@admin_controls.route('/add/tissue_specificity', methods=['POST'])
@login_required
def add_tissue_specificity():
    form = AddTissueSpecificityForm(request.form)
    form.populate_species()

    if request.method == 'POST' and form.validate():
        species_id = int(request.form.get('species_id'))
        description = request.form.get('description')

        file = request.files[form.file.name].read()

        if file != b'':
            data = file.decode("utf-8").replace("\r\n", "\n").split('\n')

            order = []
            colors = []
            conditions = []

            condition_tissue = {}

            for d in data:
                condition, tissue, color = d.split("\t")

                conditions.append(condition)

                condition_tissue[condition] = tissue

                if tissue not in order:
                    order.append(tissue)
                    colors.append(color)

            specificity_method_id = ExpressionSpecificityMethod.calculate_tissue_specificities(species_id, description,
                                                                                               condition_tissue,
                                                                                               conditions,
                                                                                               use_max=True,
                                                                                               remove_background=False)
            ConditionTissue.add(species_id, condition_tissue, order, colors, specificity_method_id)

        flash('Calculated tissue specificities for species %d' % species_id, 'success')
        return redirect(url_for('admin.index'))
    else:
        if not form.validate():
            flash('Unable to validate data, potentially missing fields', 'danger')
            return redirect(url_for('admin.index'))
        else:
            abort(405)


@admin_controls.route('/calculate_enrichment')
@login_required
def calculate_enrichment():
    """
    Controller to start GO enrichment calculations

    :return: Redirect to admin main screen
    """
    try:
        CoexpressionCluster.calculate_enrichment()
    except Exception as e:
        flash(Markup('An error occurred! Please ensure the file is <strong>correctly formatted</strong>' +
                     ' and <strong>update the counts</strong> if necessary'), 'warning')
    finally:
        flash('Successfully calculated GO enrichment for co-expression clusters', 'success')

    return redirect(url_for('admin.controls.index'))


@admin_controls.route('/delete_enrichment')
@login_required
def delete_enrichment():
    """
    Controller to delete all existing GO enrichments

    :return: Redirect to admin main screen
    """
    CoexpressionCluster.delete_enrichment()

    flash('Successfully removed GO enrichment for co-expression clusters', 'success')
    return redirect(url_for('admin.controls.index'))


@admin_controls.route('/calculate_cluster_similarity/<int:gf_method_id>')
@login_required
def calculate_cluster_similarity(gf_method_id):
    """
    Calculate similarities between co-expression clusterings based on content. Homologous genes are used to indicate the
    similarity.

    :param gf_method_id: gene family method to use for similarities
    :return: Redirect to admin main screen
    """
    CoexpressionCluster.calculate_similarities(gene_family_method_id=gf_method_id)

    flash('Successfully calculated co-expression clustering similarities', 'success')
    return redirect(url_for('admin.controls.index'))


@admin_controls.route('/delete_cluster_similarity')
@login_required
def delete_cluster_similarity():
    """
    Controller to delete all existing cluster cluster similarities

    :return: Redirect to admin main screen
    """
    CoexpressionClusterSimilarity.empty_table()

    flash('Successfully removed similarities between co-expression clusters', 'success')
    return redirect(url_for('admin.controls.index'))


@admin_controls.route('/calculate_ecc/<int:gf_method_id>')
@login_required
def calculate_ecc(gf_method_id):
    networks = ExpressionNetworkMethod.query.all()
    network_ids = [n.id for n in networks]

    ExpressionNetworkMethod.calculate_ecc(network_ids, gf_method_id)

    flash('Successfully calculated ECC', 'success')
    return redirect(url_for('admin.controls.index'))


@admin_controls.route('/export_ftp')
@login_required
def export_ftp():
    PLANET_FTP_DATA = current_app.config['PLANET_FTP_DATA']

    # Constants for the sub-folders
    SEQUENCE_PATH = os.path.join(PLANET_FTP_DATA, 'sequences')
    ANNOTATION_PATH = os.path.join(PLANET_FTP_DATA, 'annotation')
    FAMILIES_PATH = os.path.join(PLANET_FTP_DATA, 'families')
    EXPRESSION_PATH = os.path.join(PLANET_FTP_DATA, 'expression')

    export_coding_sequences(SEQUENCE_PATH)
    export_protein_sequences(SEQUENCE_PATH)

    export_go_annotation(ANNOTATION_PATH)
    export_interpro_annotation(ANNOTATION_PATH)

    export_families(FAMILIES_PATH)
    export_coexpression_clusters(EXPRESSION_PATH)
    export_expression_networks(EXPRESSION_PATH)

    flash('Successfully exported data to FTP folder', 'success')
    return redirect(url_for('admin.controls.index'))
