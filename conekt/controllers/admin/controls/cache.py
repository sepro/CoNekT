from flask import flash, url_for
from conekt.extensions import admin_required
from werkzeug.utils import redirect

from conekt import cache
from conekt.controllers.admin.controls import admin_controls


@admin_controls.route('/clear/cache')
@admin_required
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