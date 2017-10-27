from flask_admin import expose

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

        return self.render('admin/add/xrefs.html', form=form)


class AddXRefsFamiliesView(AdminBaseView):
    """
    Admin page to add external references to families
    """
    @expose('/')
    def index(self):
        form = AddXRefsFamiliesForm()
        form.populate_methods()

        return self.render('admin/add/xrefs_families.html', form=form)