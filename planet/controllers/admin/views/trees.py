from flask_admin import expose

from planet.controllers.admin.views import MyModelView,AdminBaseView
from planet.forms.admin.add_trees import AddTreesForm


class TreeMethodAdminView(MyModelView):
    """
    GeneFamilyMethod view for admins, specifies what is available in CRUD
    """
    form_columns = ('description', )
    form_edit_rules = form_columns

    column_display_pk = True

    can_create = False


class AddTreesView(AdminBaseView):
    """
    Admin page to add human readable descriptions to genes
    """
    @expose('/')
    def index(self):
        form = AddTreesForm()
        form.populate_methods()

        return self.render('admin/add/trees.html', form=form)
