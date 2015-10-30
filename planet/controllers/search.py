from flask import g, Blueprint, flash, redirect, url_for, render_template
from sqlalchemy.sql import or_, and_
from sqlalchemy import func

from planet.models.sequences import Sequence
from planet.models.go import GO
from planet.models.interpro import Interpro
from planet.models.gene_families import GeneFamily
from planet.models.expression_profiles import ExpressionProfile


search = Blueprint('search', __name__)


@search.route('/keyword/<keyword>')
def search_single_keyword(keyword):
    """
    Function to perform a keyword search without a form.

    :param keyword: Keyword to look for
    """
    sequences = Sequence.query.with_entities(Sequence.id, Sequence.name)\
        .filter(Sequence.name == keyword).all()

    go = GO.query.filter(or_(GO.description.ilike("%"+keyword+"%"),
                             GO.name.ilike("%"+keyword+"%"),
                             GO.label == keyword)).all()

    interpro = Interpro.query.filter(or_(Interpro.description.ilike("%"+keyword+"%"),
                                         Interpro.label == keyword)).all()

    families = GeneFamily.query.filter(GeneFamily.name == keyword).all()
    profiles = ExpressionProfile.query.filter(ExpressionProfile.probe == keyword).all()

    # If the result is unique redirect to the corresponding page
    if len(sequences) + len(go) + len(interpro) + len(families) + len(profiles) == 1:
        if len(sequences) == 1:
            return redirect(url_for('sequence.sequence_view', sequence_id=sequences[0].id))
        elif len(go) == 1:
            return redirect(url_for('go.go_view', go_id=go[0].id))
        elif len(interpro) == 1:
            return redirect(url_for('interpro.interpro_view', interpro_id=interpro[0].id))
        elif len(families) == 1:
            return redirect(url_for('family.family_view', family_id=families[0].id))
        elif len(profiles) == 1:
            return redirect(url_for('expression_profile.expression_profile_view', profile_id=profiles[0].id))

    return render_template("search_results.html", keyword=keyword,
                           sequences=sequences,
                           go=go,
                           interpro=interpro,
                           families=families,
                           profiles=profiles)


def __search_string(term_string):
    """
    Private function to be used internally by the simple search. Performs an intuitive search on various fields.

    all terms are converted into uppercase to make searches case insensitive

    :param term_string: space-separated strings to search for
    :return: dict with results per type
    """
    terms = term_string.upper().split()

    sequences = Sequence.query.filter(Sequence.name.in_(terms)).all()

    go = GO.query.filter(or_(and_(*[GO.description.ilike("%"+term+"%") for term in terms]),
                             and_(*[GO.name.ilike("%"+term+"%") for term in terms]),
                             GO.label.in_(terms))).all()

    interpro = Interpro.query.filter(or_(and_(*[Interpro.description.ilike("%"+term+"%") for term in terms]),
                                         Interpro.label.in_(terms))).all()

    families = GeneFamily.query.filter(func.upper(GeneFamily.name).in_(terms)).all()
    profiles = ExpressionProfile.query.filter(ExpressionProfile.probe.in_(terms)).all()

    return {"go": go,
            "interpro": interpro,
            "sequences": sequences,
            "families": families,
            "profiles": profiles}


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
        results = __search_string(g.search_form.terms.data)

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
