from flask import Blueprint, redirect, url_for, render_template, g, Response

from conekt import cache
from conekt.models.clades import Clade
from conekt.models.relationships.cluster_clade import ClusterCladeEnrichment
from conekt.models.species import Species
from conekt.models.gene_families import GeneFamily
from conekt.models.interpro import Interpro

import json

clade = Blueprint('clade', __name__)


@clade.route('/')
def clade_overview():
    """
    For lack of a better alternative redirect users to the main page
    """
    return redirect(url_for('main.screen'))


@clade.route('/view/<clade_id>')
@cache.cached()
def clade_view(clade_id):
    """
    Get all information for the desired clade and return the main view

    :param clade_id: internal ID of the clade
    """
    current_clade = Clade.query.get_or_404(clade_id)

    species_codes = json.loads(current_clade.species)

    species = Species.query.filter(Species.code.in_(species_codes)).order_by(Species.name).all()

    families_count = current_clade.families.count()
    interpro_count = current_clade.interpro.count()
    cluster_count = current_clade.enriched_clusters.count()
    association_count = current_clade.sequence_sequence_clade_associations.count()

    return render_template('clade.html', clade=current_clade,
                           families_count=families_count, interpro_count=interpro_count, cluster_count=cluster_count,
                           association_count=association_count, species=species)


@clade.route('/families/<int:clade_id>/')
@clade.route('/families/<int:clade_id>/<int:page>')
@cache.cached()
def clade_families(clade_id, page=1):
    """
    Paginated list of families that emerged in this clade

    :param clade_id: internal clade ID
    :param page: page number
    :return: html-response which can be used in combination with the pagination code
    """
    current_clade = Clade.query.get_or_404(clade_id)
    families = current_clade.families.order_by(GeneFamily.name).paginate(page,
                                                                         g.page_items,
                                                                         False).items

    return render_template('pagination/families.html', families=families)


@clade.route('/families/table/<int:clade_id>')
@cache.cached()
def clade_families_table(clade_id):
    """
    Returns a table (csv) of all families that emerged in this clade

    :param clade_id: internal clade id
    :return: plain text response with csv file
    """
    families = Clade.query.get(clade_id).families.order_by(GeneFamily.name)

    return Response(render_template('tables/families.csv', families=families), mimetype='text/plain')


@clade.route('/interpro/<int:clade_id>/')
@clade.route('/interpro/<int:clade_id>/<int:page>')
@cache.cached()
def clade_interpro(clade_id, page=1):
    """
    Paginated list of InterPro domains that emerged in this clade

    :param clade_id: internal clade ID
    :param page: page number
    :return: html-response which can be used in combination with the pagination code
    """
    current_clade = Clade.query.get_or_404(clade_id)
    interpro = current_clade.interpro.order_by(Interpro.label).paginate(page,
                                                                        g.page_items,
                                                                        False).items

    return render_template('pagination/interpro.html', interpro=interpro)


@clade.route('/interpro/table/<int:clade_id>')
@cache.cached()
def clade_interpro_table(clade_id):
    """
    Returns a table (csv) of all InterPro domains that emerged in this clade

    :param clade_id: internal clade id
    :return: plain text response with csv file
    """
    interpro = Clade.query.get(clade_id).interpro.order_by(Interpro.label)

    return Response(render_template('tables/interpro.csv', interpro=interpro), mimetype='text/plain')


@clade.route('/clusters/<int:clade_id>/')
@clade.route('/clusters/<int:clade_id>/<int:page>')
@cache.cached()
def clade_clusters(clade_id, page=1):
    """
    Paginated list of clusters that are enriched for this clade

    :param clade_id: internal clade ID
    :param page: page number
    :return: html-response which can be used in combination with the pagination code
    """
    current_clade = Clade.query.get_or_404(clade_id)
    clusters = current_clade.enriched_clusters.\
        order_by(ClusterCladeEnrichment.corrected_p_value.asc()).paginate(page, g.page_items, False).items

    return render_template('pagination/clusters.html', clusters=clusters)


@clade.route('/associations/<int:clade_id>/')
@clade.route('/associations/<int:clade_id>/<int:page>')
@cache.cached()
def clade_associations(clade_id, page=1):

    current_clade = Clade.query.get_or_404(clade_id)
    associations = current_clade.sequence_sequence_clade_associations.paginate(page,
                                                                               g.page_items,
                                                                               False).items

    return render_template('pagination/clade_relations.html', relations=associations)