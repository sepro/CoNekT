"""
Everything that needs to be set up to get flask running is initialized in this file.

  * set up and configure the app

  * configure extensions (db, debugtoolbar, compress, ...)

  * load all controllers and register their blueprints to a subdomain

  * Note: as long as models are used by a controller they are loaded and included in create_db !

  * add admin panel

  * set up global things like the search form and custom 403/404 error messages
"""
from flask import Flask, render_template, g, request, url_for, flash, redirect
from flask_admin.menu import MenuLink
from flask_login import current_user
from flask_admin import Admin

from planet.extensions import toolbar, db, login_manager, cache, htmlmin, blast_thread, compress, whooshee, migrate


def create_app(config):
    # Set up app, database and login manager before importing models and controllers
    # Important for db_create script

    app = Flask(__name__)

    app.config.from_object(config)
    configure_extensions(app)
    configure_blueprints(app)
    configure_admin_panel(app)
    configure_error_handlers(app)
    configure_hooks(app)

    return app


def configure_extensions(app):
    db.app = app
    db.init_app(app)

    # Enable Whooshee
    whooshee.init_app(app)

    # Enable login manager
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    # Enable cach
    cache.init_app(app)

    # Enable Compress
    compress.init_app(app)

    # Enable HTMLMIN
    htmlmin.init_app(app)

    # Enable DebugToolBar
    toolbar.init_app(app)

    migrate.init_app(app, db=db)

    BLAST_ENABLED = app.config['BLAST_ENABLED']

    # Enable BLAST
    if BLAST_ENABLED:
        blast_thread.init_app(app)

    from planet.models.users import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.get(user_id)

    @login_manager.unauthorized_handler
    def unauthorized():
        return render_template('error/403.html'), 403


def configure_blueprints(app):
    # Import controllers and register as blueprint
    from planet.controllers.main import main
    from planet.controllers.auth import auth, no_login
    from planet.controllers.blast import blast
    from planet.controllers.sequence import sequence
    from planet.controllers.species import species
    from planet.controllers.go import go
    from planet.controllers.interpro import interpro
    from planet.controllers.family import family
    from planet.controllers.expression_cluster import expression_cluster
    from planet.controllers.expression_profile import expression_profile
    from planet.controllers.expression_network import expression_network
    from planet.controllers.search import search
    from planet.controllers.help import help
    from planet.controllers.heatmap import heatmap
    from planet.controllers.profile_comparison import profile_comparison
    from planet.controllers.custom_network import custom_network
    from planet.controllers.graph_comparison import graph_comparison
    from planet.controllers.clade import clade
    from planet.controllers.ecc import ecc
    from planet.controllers.specificity_comparison import specificity_comparison
    from planet.controllers.admin.controls import admin_controls
    from planet.controllers.tree import tree

    LOGIN_ENABLED = app.config['LOGIN_ENABLED']
    BLAST_ENABLED = app.config['BLAST_ENABLED']

    app.register_blueprint(main)
    if LOGIN_ENABLED:
        app.register_blueprint(auth, url_prefix='/auth')
        app.register_blueprint(admin_controls, url_prefix='/admin_controls')
    else:
        app.register_blueprint(no_login, url_prefix='/auth')
        app.register_blueprint(no_login, url_prefix='/admin_controls')

    if BLAST_ENABLED:
        app.register_blueprint(blast, url_prefix='/blast')

    app.register_blueprint(sequence, url_prefix='/sequence')
    app.register_blueprint(species, url_prefix='/species')
    app.register_blueprint(go, url_prefix='/go')
    app.register_blueprint(interpro, url_prefix='/interpro')
    app.register_blueprint(family, url_prefix='/family')
    app.register_blueprint(expression_cluster, url_prefix='/cluster')
    app.register_blueprint(expression_profile, url_prefix='/profile')
    app.register_blueprint(expression_network, url_prefix='/network')
    app.register_blueprint(search, url_prefix='/search')
    app.register_blueprint(help, url_prefix='/help')
    app.register_blueprint(heatmap, url_prefix='/heatmap')
    app.register_blueprint(profile_comparison, url_prefix='/profile_comparison')
    app.register_blueprint(custom_network, url_prefix='/custom_network')
    app.register_blueprint(graph_comparison, url_prefix='/graph_comparison')
    app.register_blueprint(clade, url_prefix='/clade')
    app.register_blueprint(ecc, url_prefix='/ecc')
    app.register_blueprint(specificity_comparison, url_prefix='/specificity_comparison')
    app.register_blueprint(tree, url_prefix='/tree')


def configure_admin_panel(app):
    # Admin panel
    LOGIN_ENABLED = app.config['LOGIN_ENABLED']
    if LOGIN_ENABLED:
        from planet.controllers.admin.views import MyAdminIndexView

        from planet.controllers.admin.views.ecc import ECCView
        from planet.controllers.admin.views.sequences import AddSequenceDescriptionsView
        from planet.controllers.admin.views.expression_profiles import AddExpressionProfilesView
        from planet.controllers.admin.views.expression_networks import AddCoexpressionNetworkView
        from planet.controllers.admin.views.expression_networks import ExpressionNetworkMethodAdminView
        from planet.controllers.admin.views.expression_specificity import AddSpecificityView
        from planet.controllers.admin.views.expression_specificity import ConditionTissueAdminView
        from planet.controllers.admin.views.expression_specificity import ExpressionSpecificityMethodAdminView
        from planet.controllers.admin.views.go_interpro import AddInterProView
        from planet.controllers.admin.views.go_interpro import AddGOView
        from planet.controllers.admin.views.go_interpro import AddFunctionalDataView
        from planet.controllers.admin.views.go_interpro import GOEnrichmentView
        from planet.controllers.admin.views.go_interpro import PredictGOView
        from planet.controllers.admin.views.families import AddFamiliesView, AddFamilyAnnotationView
        from planet.controllers.admin.views.families import GeneFamilyMethodAdminView
        from planet.controllers.admin.views.species import AddSpeciesView
        from planet.controllers.admin.views.species import SpeciesAdminView
        from planet.controllers.admin.views.trees import AddTreesView
        from planet.controllers.admin.views.expression_clusters import BuildNeighorhoodToClustersView
        from planet.controllers.admin.views.expression_clusters import BuildCoexpressionClustersView
        from planet.controllers.admin.views.expression_clusters import AddCoexpressionClustersView
        from planet.controllers.admin.views.expression_clusters import ClusterSimilaritiesView
        from planet.controllers.admin.views.expression_clusters import CoexpressionClusteringMethodAdminView
        from planet.controllers.admin.views.clades import AddCladesView
        from planet.controllers.admin.views.clades import CladesAdminView
        from planet.controllers.admin.views.xrefs import AddXRefsFamiliesView
        from planet.controllers.admin.views.xrefs import AddXRefsView
        from planet.controllers.admin.views.controls import ControlsView
        from planet.controllers.admin.views.news import NewsAdminView
        from planet.controllers.admin.views.trees import TreeMethodAdminView
        from planet.controllers.admin.views.trees import ReconcileTreesView

        from planet.models.users import User
        from planet.models.species import Species
        from planet.models.gene_families import GeneFamilyMethod
        from planet.models.expression.coexpression_clusters import CoexpressionClusteringMethod
        from planet.models.expression.networks import ExpressionNetworkMethod
        from planet.models.expression.specificity import ExpressionSpecificityMethod
        from planet.models.condition_tissue import ConditionTissue
        from planet.models.clades import Clade
        from planet.models.news import News
        from planet.models.trees import TreeMethod

        admin = Admin(template_mode='bootstrap3', base_template='admin/my_base.html')

        admin.init_app(app, index_view=MyAdminIndexView(template='admin/home.html'))

        # Add views used to build the database

        admin.add_view(AddSpeciesView(name='Species', endpoint='admin.add.species', url='add/species/', category='Add'))
        admin.add_view(AddSequenceDescriptionsView(name='Sequence Descriptions',
                                                   endpoint='admin.add.sequence_descriptions',
                                                   url='add/sequence_descriptions/', category='Add'))

        admin.add_menu_item(MenuLink("------------", class_name="divider", url='#'), target_category='Add')
        admin.add_menu_item(MenuLink("Functional Annotation", class_name="disabled", url="#"), target_category='Add')

        admin.add_view(AddFunctionalDataView(name='GO and InterPro definitions',
                                             endpoint='admin.add.functional_data',
                                             url='add/functional_data/', category='Add'))

        admin.add_view(AddGOView(name='GO Genes',
                                 endpoint='admin.add.go_sequences',
                                 url='add/go/', category='Add'))

        admin.add_view(AddInterProView(name='InterPro Genes',
                                       endpoint='admin.add.interpro_sequences',
                                       url='add/interpro/', category='Add'))

        admin.add_menu_item(MenuLink("------------", class_name="divider", url='#'), target_category='Add')
        admin.add_menu_item(MenuLink("Expression", class_name="disabled", url="#"), target_category='Add')

        admin.add_view(AddExpressionProfilesView(name='Expression profiles',
                                                 endpoint='admin.add.expression_profiles',
                                                 url='add/expression_profiles/', category='Add'))

        admin.add_view(AddCoexpressionNetworkView(name='Coexpression network',
                                                  endpoint='admin.add.coexpression_network',
                                                  url='add/coexpression_network/', category='Add'))

        admin.add_view(AddCoexpressionClustersView(name='Coexpression clusters',
                                                   endpoint='admin.add.coexpression_clusters',
                                                   url='add/coexpression_clusters/', category='Add'))

        admin.add_view(AddSpecificityView(name='Expression Specificity',
                                          endpoint='admin.add.expression_specificity',
                                          url='add/expression_specificity/', category='Add'))

        admin.add_menu_item(MenuLink("------------", class_name="divider", url='#'), target_category='Add')
        admin.add_menu_item(MenuLink("Comparative Genomics", class_name="disabled", url="#"), target_category='Add')

        admin.add_view(AddFamiliesView(name='Gene Families',
                                       endpoint='admin.add.families',
                                       url='add/families/', category='Add'))

        admin.add_view(AddTreesView(name='Trees',
                                    endpoint='admin.add.trees',
                                    url='add/trees/', category='Add'))

        admin.add_view(AddCladesView(name='Clades',
                                     endpoint='admin.add.clades',
                                     url='add/clades/', category='Add'))

        admin.add_menu_item(MenuLink("------------", class_name="divider", url='#'), target_category='Add')
        admin.add_menu_item(MenuLink("Misc.", class_name="disabled", url="#"), target_category='Add')

        admin.add_view(AddXRefsView(name='XRefs Genes',
                                    endpoint='admin.add.xrefs',
                                    url='add/xrefs/', category='Add'))

        admin.add_view(AddXRefsFamiliesView(name='XRefs Families',
                                            endpoint='admin.add.xrefs_families',
                                            url='add/xrefs_families/', category='Add'))

        # Build Menu
        admin.add_menu_item(MenuLink("Update Counts", url="/admin_controls/update/counts", class_name="confirmation"),
                            target_category='Build')
        admin.add_menu_item(MenuLink("------------", class_name="divider", url='#'), target_category='Build')
        admin.add_menu_item(MenuLink("Assign Clades", url="/admin_controls/update/clades", class_name="confirmation"),
                            target_category='Build')

        admin.add_view(AddFamilyAnnotationView(name='Family-wise annotation',
                                               endpoint='admin.add.family_annotation',
                                               url='build/family_annotation/', category='Build'))

        admin.add_view(ReconcileTreesView(name='Reconcile Trees', endpoint='admin.reconcile_trees',
                                          url='build/reconciled_trees', category='Build'))

        admin.add_view(ECCView(name='Expression Context Conservations (ECC)', endpoint='admin.ecc',
                               url='build/ecc/', category='Build'))
        admin.add_menu_item(MenuLink("------------", class_name="divider", url='#'), target_category='Build')
        admin.add_menu_item(MenuLink("Co-expression Clusters", class_name="disabled", url="#"), target_category='Build')

        admin.add_view(ClusterSimilaritiesView(name='Cluster Similarities', endpoint='admin.clustersimilarities',
                                               url='build/cluster_similarities/',
                                               category='Build'))
        admin.add_view(GOEnrichmentView(name='Cluster GO Enrichment', endpoint='admin.goenrichment',
                                        url='build/go_enrichment/',
                                        category='Build'))
        admin.add_view(BuildCoexpressionClustersView(name='HCCA Clusters',
                                                     endpoint='admin.build.hcca_clusters',
                                                     url='build/hcca_clusters/', category='Build'))
        admin.add_view(BuildNeighorhoodToClustersView(name='Neighborhood to clusters',
                                                      endpoint='admin.build.neighborhood_to_clusters',
                                                      url='build/neighborhood_to_clusters/', category='Build'))
        admin.add_menu_item(MenuLink("------------", class_name="divider", url='#'), target_category='Build')
        admin.add_view(PredictGOView(name='Predict GO from neighborhood', endpoint='admin.predict.go',
                                     url='predict/go', category='Build'))

        # Control panel
        admin.add_view(ControlsView(name='Controls', endpoint='admin.controls', url='controls/'))

        # CRUD for various database tables
        admin.add_view(NewsAdminView(News, db.session,
                                     endpoint='admin.news',
                                     url='news/', category='Browse'))
        admin.add_view(SpeciesAdminView(Species, db.session, url='species/', category='Browse'))
        admin.add_view(CladesAdminView(Clade, db.session, url='clades/', category='Browse', name='Clades'))
        admin.add_view(ConditionTissueAdminView(ConditionTissue, db.session, url='condition_tissue/',
                                                category="Browse", name='Condition to Tissue'))

        admin.add_menu_item(MenuLink("------------", class_name="divider", url='#'), target_category='Browse')
        admin.add_menu_item(MenuLink("Methods", class_name="disabled", url="#"), target_category='Browse')

        admin.add_view(GeneFamilyMethodAdminView(GeneFamilyMethod, db.session, url='families/', category="Browse",
                                                 name='Gene Families'))
        admin.add_view(TreeMethodAdminView(TreeMethod, db.session, url='trees/', category="Browse",
                                           name='Tree Methods'))
        admin.add_view(ExpressionNetworkMethodAdminView(ExpressionNetworkMethod, db.session, url='networks/',
                                                        category="Browse", name='Expression Networks'))
        admin.add_view(CoexpressionClusteringMethodAdminView(CoexpressionClusteringMethod, db.session, url='clusters/',
                                                             category="Browse", name='Coexpression Clustering'))
        admin.add_view(ExpressionSpecificityMethodAdminView(ExpressionSpecificityMethod, db.session, url='specificity/',
                                                            category="Browse", name='Expression Specificity'))


def configure_error_handlers(app):
    # Custom error handler for 404 errors

    @app.errorhandler(405)
    def method_not_allowed(e):
        return render_template('error/405.html'), 405

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('error/404.html'), 404

    @app.errorhandler(403)
    def access_denied(e):
        next_page = request.url_rule
        if not current_user.is_authenticated:
            flash("Log in first...", "info")
            return redirect(url_for('auth.login', next=next_page))
        else:
            flash("Not permitted! Admin rights required.", "warning")
            return render_template('error/403.html'), 403


def configure_hooks(app):
    # Register form for basic searches, needs to be done here as it is included on every page!
    from planet.forms.search import BasicSearchForm

    LOGIN_ENABLED = app.config['LOGIN_ENABLED']
    BLAST_ENABLED = app.config['BLAST_ENABLED']
    TWITTER_HANDLE = app.config['TWITTER_HANDLE'] if 'TWITTER_HANDLE' in app.config.keys() else None
    IMPRINT = app.config['IMPRINT_URL'] if 'IMPRINT_URL' in app.config.keys() else None
    PRIVACY = app.config['PRIVACY_POLICY_URL'] if 'PRIVACY_POLICY_URL' in app.config.keys() else None

    @app.before_request
    def before_request():
        g.login_enabled = LOGIN_ENABLED
        g.blast_enabled = BLAST_ENABLED
        g.search_form = BasicSearchForm()
        g.twitter_handle = TWITTER_HANDLE
        g.imprint = IMPRINT
        g.privacy = PRIVACY

        g.page_items = 30

        g.debug = app.config['DEBUG'] if 'DEBUG' in app.config else False

        if 'GLOB_MSG' in app.config and app.config['GLOB_MSG'] is not None:
            g.msg = app.config['GLOB_MSG']
            g.msg_title = app.config['GLOB_MSG_TITLE'] if 'GLOB_MSG_TITLE' in app.config else 'info'
        else:
            g.msg = None
