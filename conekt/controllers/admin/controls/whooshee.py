from flask import flash, url_for
from conekt.extensions import admin_required
from werkzeug.utils import redirect

from conekt import whooshee
from conekt.controllers.admin.controls import admin_controls


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