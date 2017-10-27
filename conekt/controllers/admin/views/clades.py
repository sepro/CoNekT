from flask_admin import expose

from conekt.controllers.admin.views import MyModelView, AdminBaseView
from conekt.forms.admin.add_clades import AddCladesForm


class CladesAdminView(MyModelView):
    """
    Clades view for admins, specifies what is available in CRUD
    """
    form_columns = ('id', 'name', 'species', 'newick_tree')

    column_display_pk = True

    can_create = True


class AddCladesView(AdminBaseView):
    """
    Admin page where all clades, in JSON, can be uploaded
    """
    @expose('/')
    def index(self):
        form = AddCladesForm()

        return self.render('admin/add/clades.html', form=form)