from flask_admin import expose

from conekt.controllers.admin.views import AdminBaseView
from conekt.forms.admin.add_sequence_descriptions import AddSequenceDescriptionsForm


class AddSequenceDescriptionsView(AdminBaseView):
    """
    Admin page to add human readable descriptions to genes
    """
    @expose('/')
    def index(self):
        form = AddSequenceDescriptionsForm()
        form.populate_species()

        return self.render('admin/add/sequence_descriptions.html', form=form)