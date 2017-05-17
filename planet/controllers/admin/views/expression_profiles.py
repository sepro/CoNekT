from flask_admin import expose

from planet.controllers.admin.views import AdminBaseView
from planet.forms.admin.add_expression_profiles import AddExpressionProfilesForm


class AddExpressionProfilesView(AdminBaseView):
    """
    Admin page to add expression profiles for one species to the database
    """
    @expose('/')
    def index(self):
        form = AddExpressionProfilesForm()
        form.populate_species()

        return self.render('admin/add/expression_profiles.html', form=form)