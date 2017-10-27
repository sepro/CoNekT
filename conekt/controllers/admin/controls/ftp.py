import os

from flask import current_app, flash, url_for
from conekt.extensions import admin_required
from werkzeug.utils import redirect

from conekt.controllers.admin.controls import admin_controls
from conekt.ftp import export_coding_sequences, export_protein_sequences, export_go_annotation, \
    export_interpro_annotation, export_families, export_coexpression_clusters, export_expression_networks


@admin_controls.route('/export_ftp')
@admin_required
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