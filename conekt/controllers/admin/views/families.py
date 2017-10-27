from flask_admin import expose

from conekt.controllers.admin.views import MyModelView, AdminBaseView
from conekt.models.gene_families import GeneFamilyMethod
from conekt.forms.admin.add_family import AddFamiliesForm


class GeneFamilyMethodAdminView(MyModelView):
    """
    GeneFamilyMethod view for admins, specifies what is available in CRUD
    """
    form_columns = ('method', )
    form_edit_rules = form_columns

    column_display_pk = True

    can_create = False


class AddFamiliesView(AdminBaseView):
    """
    Admin page to add gene families to the database
    """
    @expose('/')
    def index(self):
        form = AddFamiliesForm()

        return self.render('admin/add/families.html', form=form)


class AddFamilyAnnotationView(AdminBaseView):
    """
    Admin page to add gene families to the database
    """

    @expose('/')
    def index(self):
        methods = GeneFamilyMethod.query.all()

        return self.render('admin/add/family_annotation.html', methods=methods)
