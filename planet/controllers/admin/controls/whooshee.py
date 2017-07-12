from flask import flash, url_for
from planet.extensions import admin_required
from werkzeug.utils import redirect

from planet import whooshee
from planet.controllers.admin.controls import admin_controls


@admin_controls.route('/reindex/whooshee')
@admin_required
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