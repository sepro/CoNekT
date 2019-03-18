from flask_admin import expose

from conekt.controllers.admin.views import MyModelView, AdminBaseView
from conekt.forms.admin.add_trees import AddTreesForm, AddGeneralTreesForm
from conekt.forms.admin.reconcile_trees import ReconcileTreesForm


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

        form2 = AddGeneralTreesForm()
        form2.populate_methods()

        return self.render('admin/add/trees.html',
                           form=form,
                           form2=form2)


class ReconcileTreesView(AdminBaseView):
    """
    Admin page to add human readable descriptions to genes
    """
    @expose('/')
    def index(self):
        form = ReconcileTreesForm()
        form.populate_methods()

        return self.render('admin/build/reconcile_trees.html', form=form)
