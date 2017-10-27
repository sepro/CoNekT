from flask import flash, url_for
from conekt.extensions import admin_required
from werkzeug.utils import redirect

from conekt.controllers.admin.controls import admin_controls
from conekt.models.blast_db import BlastDB


@admin_controls.route('/build_blast_db')
@admin_required
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