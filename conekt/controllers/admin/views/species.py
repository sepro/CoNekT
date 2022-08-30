from flask_admin import expose

from conekt.controllers.admin.views import MyModelView, AdminBaseView
from conekt.forms.admin.add_species import AddSpeciesForm


class SpeciesAdminView(MyModelView):
    """
    Species view in admin page, specifies what is available in CRUD
    """

    form_columns = ("code", "name", "data_type", "color", "highlight", "description")
    form_create_rules = form_columns
    form_edit_rules = form_columns

    column_display_pk = True

    def create_model(self, form):
        model = self.model(
            form.code.data,
            form.name.data,
            form.project_page.data,
            form.color.data,
            form.highlight.data,
            form.description.data,
        )
        form.populate_obj(model)
        self.session.add(model)
        self._on_model_change(form, model, True)
        self.session.commit()
        return True


class AddSpeciesView(AdminBaseView):
    """
    Admin page to add a new species to the database
    """

    @expose("/")
    def index(self):
        form = AddSpeciesForm()

        return self.render("admin/add/species.html", form=form)
