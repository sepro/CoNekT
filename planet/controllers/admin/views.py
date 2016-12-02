from flask import flash, Markup

from flask_admin.contrib.sqla import ModelView
from flask_admin import AdminIndexView, expose, BaseView

from flask_login import current_user

from planet.forms.admin.add_species import AddSpeciesForm
from planet.forms.admin.add_go_interpro import AddFunctionalDataForm
from planet.forms.admin.add_go_sequences import AddGOForm
from planet.forms.admin.add_interpro_sequences import AddInterProForm
from planet.forms.admin.add_xrefs import AddXRefsForm, AddXRefsFamiliesForm
from planet.forms.admin.add_family import AddFamiliesForm
from planet.forms.admin.add_expression_profiles import AddExpressionProfilesForm
from planet.forms.admin.add_coexpression_clusters import AddCoexpressionClustersForm
from planet.forms.admin.add_coexpression_network import AddCoexpressionNetworkForm
from planet.forms.admin.add_clades import AddCladesForm
from planet.forms.admin.add_expression_specificity import AddConditionSpecificityForm, AddTissueSpecificityForm


class AdminBaseView(BaseView):
    def is_accessible(self):
        """
        Override to ensure the current user is an admin
        """
        return current_user.is_authenticated and current_user.is_administrator


class MyAdminIndexView(AdminIndexView):
    def is_accessible(self):
        """
        Override to ensure the current user is an admin
        """
        return current_user.is_authenticated and current_user.is_administrator


class MyModelView(ModelView):
    def is_accessible(self):
        """
        Override to ensure the current user is an admin
        """
        return current_user.is_authenticated and current_user.is_administrator

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


class ExpressionSpecificityMethodAdminView(MyModelView):
    """
    ExpressionNetworkMethod view for admins, specifies what is available in CRUD
    """
    form_columns = ('description', 'conditions', 'species')

    column_display_pk = True

    can_create = False


class CoexpressionClusteringMethodAdminView(MyModelView):
    """
    CoexpressionClusteringMethod view for admins, specifies what is available in CRUD
    """
    form_columns = ('method', 'network_method')

    column_display_pk = True

    can_create = False


class ConditionTissueAdminView(MyModelView):
    """
    ConditionTissue view for admins, specifies what is available in CRUD
    """
    column_display_pk = True

    can_create = False


class CladesAdminView(MyModelView):
    """
    Clades view for admins, specifies what is available in CRUD
    """
    form_columns = ('id', 'name', 'species', 'newick_tree')

    column_display_pk = True

    can_create = True


class ControlsView(AdminBaseView):
    @expose('/')
    def index(self):
        message = Markup('<strong>Note: </strong> some operations on this page can take a long time and slow down the '
                         'database. This can effect the user-experience of others negatively.<br />Also avoid running '
                         'multiple updates simultaniously.')
        flash(message, 'danger')

        return self.render('admin/controls.html')


class AddSpeciesView(AdminBaseView):
    @expose('/')
    def index(self):
        form = AddSpeciesForm()

        return self.render('admin/add/species.html', form=form)


class AddFunctionalDataView(AdminBaseView):
    @expose('/')
    def index(self):
        form = AddFunctionalDataForm()

        return self.render('admin/add/functional_data.html', form=form)


class AddGOView(AdminBaseView):
    @expose('/')
    def index(self):
        form = AddGOForm()
        form.populate_species()

        return self.render('admin/add/go.html', form=form)


class AddInterProView(AdminBaseView):
    @expose('/')
    def index(self):
        form = AddInterProForm()
        form.populate_species()

        return self.render('admin/add/interpro.html', form=form)


class AddXRefsView(AdminBaseView):
    @expose('/')
    def index(self):
        form = AddXRefsForm()
        form.populate_species()

        return self.render('admin/add/xrefs.html', form=form)


class AddXRefsFamiliesView(AdminBaseView):
    @expose('/')
    def index(self):
        form = AddXRefsFamiliesForm()
        form.populate_methods()

        return self.render('admin/add/xrefs_families.html', form=form)


class AddFamiliesView(AdminBaseView):
    @expose('/')
    def index(self):
        form = AddFamiliesForm()

        return self.render('admin/add/families.html', form=form)


class AddExpressionProfilesView(AdminBaseView):
    @expose('/')
    def index(self):
        form = AddExpressionProfilesForm()
        form.populate_species()

        return self.render('admin/add/expression_profiles.html', form=form)


class AddCoexpressionNetworkView(AdminBaseView):
    @expose('/')
    def index(self):
        form = AddCoexpressionNetworkForm()
        form.populate_species()

        return self.render('admin/add/coexpression_network.html', form=form)


class AddSpecificityView(AdminBaseView):
    @expose('/')
    def index(self):
        condition_form = AddConditionSpecificityForm()
        condition_form.populate_species()

        tissue_form = AddTissueSpecificityForm()
        tissue_form.populate_species()

        return self.render('admin/add/expression_specificity.html',
                           condition_form=condition_form,
                           tissue_form=tissue_form)


class AddCoexpressionClustersView(AdminBaseView):
    @expose('/')
    def index(self):
        form = AddCoexpressionClustersForm()
        form.populate_networks()

        return self.render('admin/add/coexpression_clusters.html', form=form)


class AddCladesView(AdminBaseView):
    @expose('/')
    def index(self):
        form = AddCladesForm()

        return self.render('admin/add/clades.html', form=form)