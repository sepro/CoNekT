import json

from flask import g, Blueprint, flash, request, redirect, url_for, render_template, Response
from sqlalchemy import func
from sqlalchemy.sql import or_

from planet import cache
from planet.forms.search_enriched_clusters import SearchEnrichedClustersForm
from planet.forms.search_specific_profiles import SearchSpecificProfilesForm
from planet.models.expression.specificity import ExpressionSpecificityMethod, ExpressionSpecificity
from planet.models.go import GO
from planet.models.search import Search
from planet.models.species import Species
from planet.models.sequences import Sequence

search = Blueprint('search', __name__)


@search.route('/keyword/<keyword>')
@cache.cached()
def search_single_keyword(keyword):
    """
    Function to perform a keyword search without a form.

    :param keyword: Keyword to look for
    """
    results = Search.keyword(keyword)

    # If the result is unique redirect to the corresponding page
    if len(results["sequences"]) + len(results["go"]) + len(results["interpro"]) + len(results["families"]) + len(results["profiles"]) == 1:
        if len(results["sequences"]) == 1:
            return redirect(url_for('sequence.sequence_view', sequence_id=results["sequences"][0].id))
        elif len(results["go"]) == 1:
            return redirect(url_for('go.go_view', go_id=results["go"][0].id))
        elif len(results["interpro"]) == 1:
            return redirect(url_for('interpro.interpro_view', interpro_id=results["interpro"][0].id))
        elif len(results["families"]) == 1:
            return redirect(url_for('family.family_view', family_id=results["families"][0].id))
        elif len(results["profiles"]) == 1:
            return redirect(url_for('expression_profile.expression_profile_view', profile_id=results["profiles"][0].id))

    return render_template("search_results.html", keyword=keyword,
                           go=results["go"],
                           interpro=results["interpro"],
                           sequences=results["sequences"],
                           families=results["families"],
                           profiles=results["profiles"])


@search.route('/', methods=['GET', 'POST'])
def simple():
    """
    Simple search function, is started from the nav bars search box.

    IMPORTANT: g.search_form needs to be defined globally (cfr. in the planet package __init__.py) !
    """
    if not g.search_form.validate_on_submit():
        flash("Empty search term", "warning")
        return redirect(url_for('main.screen'))
    else:
        results = Search.simple(g.search_form.terms.data)

        # If the result is unique redirect to the corresponding page
        if len(results["sequences"]) + len(results["go"]) + \
                len(results["interpro"]) + len(results["families"]) + len(results["profiles"]) == 1:

            if len(results["sequences"]) == 1:
                return redirect(url_for('sequence.sequence_view', sequence_id=results["sequences"][0].id))
            elif len(results["go"]) == 1:
                return redirect(url_for('go.go_view', go_id=results["go"][0].id))
            elif len(results["interpro"]) == 1:
                return redirect(url_for('interpro.interpro_view', interpro_id=results["interpro"][0].id))
            elif len(results["families"]) == 1:
                return redirect(url_for('family.family_view', family_id=results["families"][0].id))
            elif len(results["profiles"]) == 1:
                return redirect(url_for('expression_profile.expression_profile_view',
                                        profile_id=results["profiles"][0].id))

        return render_template("search_results.html", keyword=g.search_form.terms.data,
                               go=results["go"],
                               interpro=results["interpro"],
                               sequences=results["sequences"],
                               families=results["families"],
                               profiles=results["profiles"])


@search.route('/json/genes/<label>')
@cache.cached()
def search_json_genes(label):
    """
    This search function is used by the cytoscape.js GUI we implemented. It will look for genes with a specific GO
    label associated with them. It will return a JSON object

    :param label: GO-label to look for
    :return: JSON object with gene IDs that can be used by our GUI
    """
    output = []
    current_go = GO.query.filter_by(label=label).first()

    if current_go is not None:
        for association in current_go.sequence_associations:
            output.append(association.sequence_id)

    return Response(json.dumps(output), mimetype='application/json')


@search.route('/enriched/clusters', methods=['GET', 'POST'])
def search_enriched_clusters():
    """
    Search function to find clusters enriched with a specific GO term
    """
    form = SearchEnrichedClustersForm(request.form)
    form.populate_form()

    if request.method == 'POST':
        term = request.form.get('go_term')
        method = request.form.get('method')

        check_enrichment = request.form.get('check_enrichment') == 'y'
        check_p = request.form.get('check_p') == 'y'
        check_corrected_p = request.form.get('check_corrected_p') == 'y'

        min_enrichment = request.form.get('min_enrichment') if check_enrichment else None
        max_p = request.form.get('max_p') if check_p else None
        max_corrected_p = request.form.get('max_corrected_p') if check_corrected_p else None

        go = GO.query.filter(or_(GO.name == term,
                                 GO.label == term)).all()

        results = []

        for g in go:
            clusters = Search.enriched_clusters(g.id,
                                                method=method,
                                                min_enrichment=min_enrichment,
                                                max_p=max_p,
                                                max_corrected_p=max_corrected_p)
            results.append({'go': g, 'clusters': clusters})

        return render_template("search_enriched_clusters.html", results=results)
    else:
        return render_template("search_enriched_clusters.html", form=form)


@search.route('/specific/profiles', methods=['GET', 'POST'])
def search_specific_profiles():
    """
    Controller that shows the search form to find condition/tissue specific expressed genes

    :return: Html response
    """
    form = SearchSpecificProfilesForm(request.form)
    form.populate_form()

    if request.method == 'GET':
        return render_template("search_specific_profiles.html", form=form)
    else:
        species_id = request.form.get('species')
        method_id = request.form.get('methods')
        condition = request.form.get('conditions')
        cutoff = request.form.get('cutoff')

        species = Species.query.get_or_404(species_id)
        method = ExpressionSpecificityMethod.query.get_or_404(method_id)
        results = ExpressionSpecificity.query.filter_by(method_id=method_id, condition=condition).filter(ExpressionSpecificity.score>=cutoff)

        return render_template("search_specific_profiles.html", results=results, species=species, method=method, condition=condition)


@search.route('/specific/profiles/json')
def search_specific_profiles_json():
    """
    Controller that fetches the data for available methods

    :param species_id: species
    :return: JSON object with available methods
    """
    species = Species.query.all()
    methods = ExpressionSpecificityMethod.query.order_by(ExpressionSpecificityMethod.menu_order).all()

    output = [{'id': s.id,
               'name': s.name,
               'methods': [{'id': m.id,
                            'description': m.description,
                            'conditions': json.loads(m.conditions)} for m in methods if m.species_id == s.id]
               } for s in species]

    return Response(json.dumps(output), mimetype='application/json')


@search.route('/specific/profiles/methods/<int:species_id>')
def search_specific_profiles_methods(species_id):
    """
    Controller that fetches the data for available methods

    :param species_id: species
    :return: JSON object with available methods
    """
    methods = ExpressionSpecificityMethod.query.filter_by(species_id=species_id).order_by(ExpressionSpecificityMethod.menu_order).all()

    return Response(json.dumps([{'id': m.id,
                                 'description': m.description,
                                 'conditions': json.loads(m.conditions)
                                 } for m in methods]), mimetype='application/json')


@search.route('/typeahead/go/<term>.json')
@cache.cached()
def search_typeahead_go(term):
    """
    Controller required for populating predictive search forms using typeahead.js.

    :param term: partial search term
    :return: JSON object compatible with typeahead.js
    """
    go = GO.query.filter(GO.obsolete == 0).filter(GO.name.ilike("%"+term+"%")).order_by(func.length(GO.name)).all()

    return Response(json.dumps([{'value': g.name, 'tokens': g.name.split()} for g in go]), mimetype='application/json')


@search.route('/typeahead/go/prefetch')
@cache.cached()
def search_typeahead_prefetch():
    """
    Controller returning a small subset of GO terms (the short ones) to be used as the prefetched data for typeahead.js

    :return: JSON object compatible with typeahead.js
    """
    go = GO.query.filter(GO.obsolete == 0).filter(func.length(GO.name) < 7).order_by(func.length(GO.name)).all()

    return Response(json.dumps([{'value': g.name, 'tokens': g.name.split()} for g in go]), mimetype='application/json')


@search.route('/whooshee/<keyword>')
def search_whooshee(keyword):
    results = Sequence.query.whooshee_search(keyword).all()

    return Response(json.dumps([r.name for r in results]), mimetype='application/json')
