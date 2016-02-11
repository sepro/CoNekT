from flask import Blueprint, redirect, url_for, render_template, g, Response

from planet import cache
from planet.models.clades import Clade
from planet.models.species import Species
from planet.models.gene_families import GeneFamily
from planet.models.interpro import Interpro

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
    Get a sequence based on the ID and show the details for this sequence

    :param sequence_id: ID of the sequence
    """
    current_clade = Clade.query.get_or_404(clade_id)

    species_codes = json.loads(current_clade.species)

    species = Species.query.filter(Species.code.in_(species_codes)).order_by(Species.name).all()

    families_count = current_clade.families.count()
    interpro_count = current_clade.interpro.count()

    return render_template('clade.html', clade=current_clade,
                           families_count=families_count, interpro_count=interpro_count,
                           species=species)


@clade.route('/families/<int:clade_id>/')
@clade.route('/families/<int:clade_id>/<int:page>')
@cache.cached()
def clade_families(clade_id, page=1):

    current_clade = Clade.query.get_or_404(clade_id)
    families = current_clade.families.order_by(GeneFamily.name).paginate(page,
                                                                         g.page_items,
                                                                         False).items

    return render_template('pagination/families.html', families=families)


@clade.route('/families/table/<int:clade_id>')
@cache.cached()
def clade_families_table(clade_id):

    families = Clade.query.get(clade_id).families.order_by(GeneFamily.name)

    return Response(render_template('tables/families.csv', families=families), mimetype='text/plain')


@clade.route('/interpro/<int:clade_id>/')
@clade.route('/interpro/<int:clade_id>/<int:page>')
@cache.cached()
def clade_interpro(clade_id, page=1):

    current_clade = Clade.query.get_or_404(clade_id)
    interpro = current_clade.interpro.order_by(Interpro.label).paginate(page,
                                                                        g.page_items,
                                                                        False).items

    return render_template('pagination/interpro.html', interpro=interpro)


@clade.route('/interpro/table/<int:clade_id>')
@cache.cached()
def clade_interpro_table(clade_id):

    interpro = Clade.query.get(clade_id).interpro.order_by(Interpro.label)

    return Response(render_template('tables/interpro.csv', interpro=interpro), mimetype='text/plain')
