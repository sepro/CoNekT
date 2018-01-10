import json

from flask import g, Blueprint, flash, request, redirect, url_for, render_template, Response, current_app
from sqlalchemy import func
from sqlalchemy.sql import or_, and_
from sqlalchemy.orm import joinedload

from conekt import cache
from conekt.forms.search_enriched_clusters import SearchEnrichedClustersForm
from conekt.forms.search_specific_profiles import SearchSpecificProfilesForm
from conekt.forms.advanced_search import AdvancedSequenceSearchForm
from conekt.models.expression.specificity import ExpressionSpecificityMethod, ExpressionSpecificity
from conekt.models.relationships.cluster_go import ClusterGOEnrichment
from conekt.models.interpro import Interpro
from conekt.models.go import GO
from conekt.models.search import Search
from conekt.models.species import Species
from conekt.models.sequences import Sequence
from conekt.models.xrefs import XRef

from utils.benchmark import benchmark
import logging

search = Blueprint('search', __name__)


@search.route('/keyword/<keyword>')
@cache.cached()
def search_single_keyword(keyword):
    """
    Function to perform a keyword search without a form.

    :param keyword: Keyword to look for
    """
    results = Search.whooshee_simple(keyword)

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
        # results = Search.simple(g.search_form.terms.data)
        results = Search.whooshee_simple(g.search_form.terms.data)

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


@search.route('/advanced', methods=['GET', 'POST'])
def advanced():

    adv_sequence_form = AdvancedSequenceSearchForm(request.form)
    adv_sequence_form.populate_species()
    adv_sequence_form.populate_gf_methods()

    if request.method == 'GET':
        return render_template("search_advanced.html", adv_sequence_form=adv_sequence_form)
    else:
        species_id = int(request.form.get('species'))

        gene_ids = request.form.get('gene_ids')

        terms = request.form.get('adv_terms')
        terms_rules = request.form.get('terms_rules')

        gene_family_method_id = int(request.form.get('gene_family_method'))
        gene_families = request.form.get('gene_families').split()

        go_rules = request.form.get('go_rules')
        go_terms = [gt.data['go_term'] for gt in adv_sequence_form.go_terms.entries if gt.data['go_term'] != ""]
        include_predictions = request.form.get('include_predictions') == 'y'

        interpro_rules = request.form.get('interpro_rules')
        interpro_terms = [it.data['interpro_domain']
                          for it in adv_sequence_form.interpro_domains.entries if it.data['interpro_domain'] != ""]

        results = Search.advanced_sequence_search(species_id,
                                                  gene_ids.strip().split(),
                                                  terms, terms_rules,
                                                  gene_family_method_id, gene_families,
                                                  go_terms, go_rules,
                                                  interpro_terms, interpro_rules, include_predictions=include_predictions)

        return render_template("search_results.html", keyword="Advanced search results",
                               sequences=results, advanced=True)


@search.route('/json/genes/<label>')
@search.route('/json/genes/')
@cache.cached()
def search_json_genes(label=''):
    """
    This search function is used by the cytoscape.js GUI we implemented. It will look for genes with a specific GO
    label associated with them. It will return a JSON object

    Note predicted GO terms are excluded

    :param label: GO-label to look for
    :return: JSON object with gene IDs that can be used by our GUI
    """
    output = []

    if len(label) > 3:
        current_go = GO.query.filter(or_(GO.label == label, GO.name == label)).all()
        current_interpro = Interpro.query.filter(Interpro.description == label).all()
    else:
        current_go = []
        current_interpro = []

    for go in current_go:
        for association in go.sequence_associations:
            # Exclude predictions
            if association.predicted == 0:
                output.append(association.sequence_id)

    for ipr in current_interpro:
        for association in ipr.sequence_associations:
            output.append(association.sequence_id)

    return Response(json.dumps(list(set(output))), mimetype='application/json')


@search.route('/enriched/count', methods=['POST'])
def count_enriched_clusters():
    """
    Counts the number of clusters enriched for a set of criteria

    :return: json response with the count
    """

    content = request.get_json(silent=True)

    try:
        term = content["go_term"]
        method = int(content["method"])

        check_enrichment = bool(content["check_enrichment"])
        check_p = bool(content["check_p"])
        check_corrected_p = bool(content["check_corrected_p"])

        min_enrichment = float(content["min_enrichment"]) if check_enrichment else None
        max_p = float(content["max_p"]) if check_p else None
        max_corrected_p = float(content["max_corrected_p"]) if check_corrected_p else None

        enable_clade_enrichment = bool(content["enable_clade_enrichment"])
        clade = int(content['clade']) if enable_clade_enrichment else None

        go = GO.query.filter(or_(GO.name == term,
                                 GO.label == term)).first()

        cluster_count = Search.count_enriched_clusters(go.id,
                                                       method=method,
                                                       min_enrichment=min_enrichment,
                                                       max_p=max_p,
                                                       max_corrected_p=max_corrected_p,
                                                       enriched_clade_id=clade)

        return Response(json.dumps({'count': cluster_count, 'error': 0}), mimetype='application/json')
    except Exception as e:
        # Bad data return zero
        return Response(json.dumps({'count': 0, 'error': 1}), mimetype='application/json')


@search.route('/enriched/clusters', methods=['GET', 'POST'])
def search_enriched_clusters():
    """
    Search function to find clusters enriched with a specific GO term
    """
    form = SearchEnrichedClustersForm(request.form)
    form.populate_form()

    if request.method == 'POST':
        term = request.form.get('go_term')
        method = int(request.form.get('method'))

        check_enrichment = request.form.get('check_enrichment') == 'y'
        check_p = request.form.get('check_p') == 'y'
        check_corrected_p = request.form.get('check_corrected_p') == 'y'

        min_enrichment = request.form.get('min_enrichment') if check_enrichment else None
        max_p = request.form.get('max_p') if check_p else None
        max_corrected_p = request.form.get('max_corrected_p') if check_corrected_p else None

        enable_clade_enrichment = request.form.get('enable_clade_enrichment') == 'y'
        clade = request.form.get('clade') if enable_clade_enrichment else None

        go = GO.query.filter(or_(GO.name == term,
                                 GO.label == term)).all()

        results = []

        for g in go:
            clusters = Search.enriched_clusters(g.id,
                                                method=method,
                                                min_enrichment=min_enrichment,
                                                max_p=max_p,
                                                max_corrected_p=max_corrected_p,
                                                enriched_clade_id=clade)
            results.append({'go': g, 'clusters': clusters})

        return render_template("find_enriched_clusters.html", results=results)
    else:

        example = {
            'go_term': None,
            'method': None,
            'max_corrected_p': '0.05'
        }

        enrichment = ClusterGOEnrichment.query.filter(ClusterGOEnrichment.corrected_p_value < 0.05).first()

        if enrichment is not None:
            example['go_term'] = enrichment.go.name
            example['method'] = enrichment.cluster.method_id

        return render_template("find_enriched_clusters.html", form=form, example=example)


@search.route('/specific/count', methods=['POST'])
def count_specific_profiles():
    """
    Counts the number of genes above a certain SPM threshold.

    :return: json response with the count
    """

    content = request.get_json(silent=True)

    try:
        method = int(content["method"])
        cutoff = float(content["cutoff"])
        condition = content["condition"]

        count = ExpressionSpecificity.query.filter(ExpressionSpecificity.method_id == method). \
            filter(ExpressionSpecificity.score >= cutoff). \
            filter(ExpressionSpecificity.condition == condition). \
            count()

        return Response(json.dumps({'count': count, 'error': 0}), mimetype='application/json')
    except Exception as e:
        # Bad data return zero
        return Response(json.dumps({'count': 0, 'error': 1}), mimetype='application/json')


@search.route('/specific/profiles', methods=['GET', 'POST'])
def search_specific_profiles():
    """
    Controller that shows the search form to find condition/tissue specific expressed genes

    :return: Html response
    """
    form = SearchSpecificProfilesForm(request.form)
    form.populate_form()

    if request.method == 'GET':
        return render_template("find_specific_profiles.html", form=form)
    else:
        species_id = request.form.get('species')
        method_id = request.form.get('methods')
        condition = request.form.get('conditions')
        cutoff = request.form.get('cutoff')

        species = Species.query.get_or_404(species_id)
        method = ExpressionSpecificityMethod.query.get_or_404(method_id)
        results = ExpressionSpecificity.query.\
            filter(ExpressionSpecificity.method_id == method_id).\
            filter(ExpressionSpecificity.score>=cutoff).\
            filter(ExpressionSpecificity.condition == condition).\
            options(
                joinedload(ExpressionSpecificity.profile).undefer("profile")
            )

        return render_template("find_specific_profiles.html", results=results, species=species, method=method, condition=condition)


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


@search.route('/typeahead/interpro/<term>.json')
@cache.cached()
def search_typeahead_interpro(term):
    """
    Controller required for populating predictive search forms using typeahead.js.

    :param term: partial search term
    :return: JSON object compatible with typeahead.js
    """
    if len(term) > 7:
        interpro = Interpro.query.filter(or_(Interpro.description.ilike("%" + term + "%"), Interpro.label.ilike(term + "%"))).order_by(
            func.length(Interpro.description)).all()
    else:
        interpro = Interpro.query.filter(Interpro.description.ilike("%"+term+"%")).order_by(func.length(Interpro.description)).all()

    return Response(json.dumps([{'value': i.description, 'tokens': i.description.split() + [i.label], 'label': i.label} for i in interpro]),
                    mimetype='application/json')


@search.route('/typeahead/interpro/prefetch')
@cache.cached()
def search_typeahead_prefetch_interpro():
    """
    Controller returning a small subset of GO terms (the short ones) to be used as the prefetched data for typeahead.js

    :param term: partial search term
    :return: JSON object compatible with typeahead.js
    """
    interpro = Interpro.query.filter(func.length(Interpro.description) < 7).order_by(func.length(Interpro.description)).all()

    return Response(json.dumps([{'value': i.description, 'tokens': i.description.split() + [i.label], 'label': i.label} for i in interpro]),
                    mimetype='application/json')


@search.route('/typeahead/go/<term>.json')
@cache.cached()
def search_typeahead_go(term):
    """
    Controller required for populating predictive search forms using typeahead.js.

    :param term: partial search term
    :return: JSON object compatible with typeahead.js
    """
    if term.lower().startswith('go:') and len(term) > 7:
        go = GO.query.filter(GO.obsolete == 0).filter(GO.label.ilike(term + "%")).all()
    else:
        go = GO.query.filter(GO.obsolete == 0).filter(GO.name.ilike("%"+term+"%")).order_by(func.length(GO.name)).all()

    return Response(json.dumps([{'value': g.name, 'tokens': g.name.split() + [g.label], 'label': g.label} for g in go]),
                    mimetype='application/json')


@search.route('/typeahead/go/prefetch')
@cache.cached()
def search_typeahead_prefetch_go():
    """
    Controller returning a small subset of GO terms (the short ones) to be used as the prefetched data for typeahead.js

    :return: JSON object compatible with typeahead.js
    """
    go = GO.query.filter(GO.obsolete == 0).filter(func.length(GO.name) < 7).order_by(func.length(GO.name)).all()

    return Response(json.dumps([{'value': g.name, 'tokens': g.name.split() + [g.label], 'label': g.label} for g in go]),
                    mimetype='application/json')


@search.route('/whooshee/<keyword>')
@cache.cached()
def search_whooshee(keyword):
    results = Sequence.query.whooshee_search(keyword).all()

    return Response(json.dumps([r.name for r in results]), mimetype='application/json')


@search.route('/no_whooshee/<keyword>')
@cache.cached()
def search_no_whooshee(keyword):
    results = Sequence.query.filter(Sequence.description.ilike("%" + keyword + "%")).all()

    return Response(json.dumps([r.name for r in results]), mimetype='application/json')
