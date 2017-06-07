from flask_admin import expose

from planet.controllers.admin.views import AdminBaseView
from planet.forms.admin.add_trees import AddTreesForm


class AddTreesView(AdminBaseView):
    """
    Admin page to add human readable descriptions to genes
    """
    @expose('/')
    def index(self):
        form = AddTreesForm()
        form.populate_methods()

        return self.render('admin/add/trees.html', form=form)
