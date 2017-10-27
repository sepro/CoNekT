from flask_admin import expose

from conekt.controllers.admin.views import MyModelView, AdminBaseView
from conekt.forms.admin.add_coexpression_network import AddCoexpressionNetworkForm


class ExpressionNetworkMethodAdminView(MyModelView):
    """
    ExpressionNetworkMethod view for admins, specifies what is available in CRUD
    """
    form_columns = ('description', 'edge_type', 'species')

    column_display_pk = True

    can_create = False


class AddCoexpressionNetworkView(AdminBaseView):
    """
    Admin page to add the co-expression network for one species.

    Note: the input is a full PCC co-expression network, however, prior to adding the network HR Ranks are
    calculated and used as an additional filter.
    """
    @expose('/')
    def index(self):
        form = AddCoexpressionNetworkForm()
        form.populate_species()

        return self.render('admin/add/coexpression_network.html', form=form)