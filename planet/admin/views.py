from flask.ext.admin.contrib.sqla import ModelView
from flask.ext.admin import AdminIndexView

from flask.ext.login import current_user


class MyAdminIndexView(AdminIndexView):
    def is_accessible(self):
        """
        Override to ensure the current user is an admin
        """
        return current_user.is_authenticated() and current_user.is_administrator()


class MyModelView(ModelView):
    def is_accessible(self):
        """
        Override to ensure the current user is an admin
        """
        return current_user.is_authenticated() and current_user.is_administrator()

    def _get_endpoint(self, endpoint):
        """
        Override to rename views (and avoid clash with blueprints in the app itself)
        """
        if endpoint:
            return endpoint

        return '%s' % self.__class__.__name__.lower()


class SpeciesAdminView(MyModelView):
    """
    Species view in admin page, specifies what is available in CRUD
    """
    form_columns = ('code', 'name', 'data_type', 'ncbi_tax_id',
                    'pubmed_id', 'project_page', 'color', 'highlight', )
    form_create_rules = form_columns
    form_edit_rules = form_columns

    column_display_pk = True

    def create_model(self, form):
        model = self.model(form.code.data,
                           form.name.data,
                           form.data_type.data,
                           form.ncbi_tax_id.data,
                           form.pubmed_id.data,
                           form.project_page.data,
                           form.color.data,
                           form.highlight.data)
        form.populate_obj(model)
        self.session.add(model)
        self._on_model_change(form, model, True)
        self.session.commit()
        return True


class GeneFamilyMethodAdminView(MyModelView):
    """
    GeneFamilyMethod view for admins, specifies what is available in CRUD
    """
    form_columns = ('method', )
    form_edit_rules = form_columns

    column_display_pk = True

    can_create = False


class ExpressionNetworkMethodAdminView(MyModelView):
    """
    ExpressionNetworkMethod view for admins, specifies what is available in CRUD
    """
    form_columns = ('description', 'edge_type', 'species')

    column_display_pk = True

    can_create = False


class CoexpressionClusteringMethodAdminView(MyModelView):
    """
    CoexpressionClusteringMethod view for admins, specifies what is available in CRUD
    """
    form_columns = ('method', 'network_method')

    column_display_pk = True

    can_create = False

class CladesAdminView(MyModelView):
    """
    CoexpressionClusteringMethod view for admins, specifies what is available in CRUD
    """
    form_columns = ('id', 'name', 'species', 'newick_tree')

    column_display_pk = True

    can_create = True