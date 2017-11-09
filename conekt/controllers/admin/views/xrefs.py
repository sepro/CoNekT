from flask_admin import expose
from flask import current_app, flash

from conekt.controllers.admin.views import AdminBaseView
from conekt.forms.admin.add_xrefs import AddXRefsForm, AddXRefsFamiliesForm


class AddXRefsView(AdminBaseView):
    """
    Admin page to add external references to genes
    """
    @expose('/')
    def index(self):
        form = AddXRefsForm()
        form.populate_species()

        if current_app.config['WHOOSHEE_ENABLE_INDEXING']:
            flash("WHOOSHEE Indexing is enabled, this can take a long time to complete.", "warning")

        return self.render('admin/add/xrefs.html', form=form)


class AddXRefsFamiliesView(AdminBaseView):
    """
    Admin page to add external references to families
    """
    @expose('/')
    def index(self):
        form = AddXRefsFamiliesForm()
        form.populate_methods()

        if current_app.config['WHOOSHEE_ENABLE_INDEXING']:
            flash("WHOOSHEE Indexing is enabled, this can take a long time to complete.", "warning")

        return self.render('admin/add/xrefs_families.html', form=form)