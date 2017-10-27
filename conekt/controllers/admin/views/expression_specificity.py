from flask_admin import expose

from conekt.controllers.admin.views import MyModelView, AdminBaseView
from conekt.forms.admin.add_expression_specificity import AddConditionSpecificityForm, AddTissueSpecificityForm


class ExpressionSpecificityMethodAdminView(MyModelView):
    """
    ExpressionNetworkMethod view for admins, specifies what is available in CRUD
    """
    form_columns = ('description', 'conditions', 'species', 'menu_order')

    column_display_pk = True

    can_create = False


class ConditionTissueAdminView(MyModelView):
    """
    ConditionTissue view for admins, specifies what is available in CRUD
    """
    column_display_pk = True

    can_create = False


class AddSpecificityView(AdminBaseView):
    """
    Admin page to calculate condition specificities (no additional input required) or more general specificities
    (file linking condition to more general condition/tissue/... required)
    """
    @expose('/')
    def index(self):
        condition_form = AddConditionSpecificityForm()
        condition_form.populate_species()

        tissue_form = AddTissueSpecificityForm()
        tissue_form.populate_species()

        return self.render('admin/add/expression_specificity.html',
                           condition_form=condition_form,
                           tissue_form=tissue_form)