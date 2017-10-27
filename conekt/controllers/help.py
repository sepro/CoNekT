from flask import Blueprint, render_template, abort

from conekt import cache

# Dict containing all keywords and the template with the information
__TOPICS = {"gene_family": "modals/help/gene_family.html",
            "interpro_domain": "modals/help/interpro_domain.html",
            "go": "modals/help/go.html",
            "correction": "modals/help/fdr.html",
            "fdr": "modals/help/fdr.html",
            "ecc": "modals/help/ecc.html",
            "spm": "modals/help/spm.html",
            "entropy": "modals/help/entropy.html",
            "tau": "modals/help/tau.html",
            "cluster": "modals/help/cluster.html",
            "neighborhood": "modals/help/neighborhood.html",
            "hrr": "modals/help/hrr.html",
            "blast": "modals/help/blast.html",
            "pcc": "modals/help/pcc.html",
            "lowabundance": "modals/help/low_abundance.html"}

__POPUPS = {"lowabundance": "tooltips/low_abundance.html"}

help = Blueprint('help', __name__)


@help.route('/<topic>')
@cache.cached()
def help_topic(topic):
    """
    Generic function to get help modals.

    :param topic: name of the topic
    :return: renders template for the topic if found, 404 if not.
    """
    if topic in __TOPICS.keys():
        return render_template(__TOPICS[topic])
    else:
        abort(404)


@help.route('/popup/<topic>')
@cache.cached()
def help_popup(topic):
    """
    Generic function to get help popups

    :param topic: name of the topic
    :return: renders template for the topic if found, 404 if not.
    """
    if topic in __POPUPS.keys():
        return render_template(__POPUPS[topic])
    else:
        abort(404)

