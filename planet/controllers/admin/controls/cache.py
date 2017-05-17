from flask import flash, url_for
from flask_login import login_required
from werkzeug.utils import redirect

from planet import cache
from planet.controllers.admin.controls import admin_controls


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