from flask import flash
from flask_admin import expose
from markupsafe import Markup

from conekt.controllers.admin.views import AdminBaseView
from conekt.models.gene_families import GeneFamilyMethod


class ECCView(AdminBaseView):
    """
    Control panel for administrators. Contains links to
    """
    @expose('/')
    def index(self):
        message = Markup('<strong>Note: </strong> some operations on this page can take a long time and slow down the '
                         'database. This can effect the user-experience of others negatively.<br />Also avoid running '
                         'multiple updates simultaniously.')
        flash(message, 'danger')

        gene_family_methods = GeneFamilyMethod.query.all()

        return self.render('admin/build/ecc.html', gene_family_methods=gene_family_methods)