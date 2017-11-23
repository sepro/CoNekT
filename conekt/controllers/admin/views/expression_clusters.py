from flask import flash
from flask_admin import expose
from markupsafe import Markup

from conekt.controllers.admin.views import MyModelView, AdminBaseView
from conekt.forms.admin.add_coexpression_clusters import AddCoexpressionClustersForm
from conekt.forms.admin.build_coexpression_clusters import BuildCoexpressionClustersForm
from conekt.forms.admin.neighborhood_to_clusters import NeighborhoodToClustersForm
from conekt.models.gene_families import GeneFamilyMethod


class CoexpressionClusteringMethodAdminView(MyModelView):
    """
    CoexpressionClusteringMethod view for admins, specifies what is available in CRUD
    """
    form_columns = ('method', 'network_method')

    column_display_pk = True

    can_create = False


class ClusterSimilaritiesView(AdminBaseView):
    """
    Control panel for administrators. Contains links to start computing cluster similarities
    """
    @expose('/')
    def index(self):
        message = Markup('<strong>Note: </strong> some operations on this page can take a long time and slow down the '
                         'database. This can effect the user-experience of others negatively.<br />Also avoid running '
                         'multiple updates simultaniously.')
        flash(message, 'danger')

        gene_family_methods = GeneFamilyMethod.query.all()

        return self.render('admin/build/cluster_similarities.html', gene_family_methods=gene_family_methods)


class AddCoexpressionClustersView(AdminBaseView):
    """
    Add Coexpression clusters, computed outside of PlaNet, to the database
    """
    @expose('/')
    def index(self):
        form = AddCoexpressionClustersForm()
        form.populate_networks()

        return self.render('admin/add/coexpression_clusters.html', form=form)


class BuildCoexpressionClustersView(AdminBaseView):
    """
    Build HCCA clusters, based on an existing network.

    Note: Computing the clusters is done on the server. This might cause a high load for the duration of the
    calculations
    """
    @expose('/')
    def index(self):
        form = BuildCoexpressionClustersForm()
        form.populate_networks()

        return self.render('admin/build/coexpression_clusters.html', form=form)


class BuildNeighorhoodToClustersView(AdminBaseView):
    @expose('/')
    def index(self):
        form = NeighborhoodToClustersForm()
        form.populate_networks()

        return self.render('admin/build/neighborhood_to_clusters.html', form=form)