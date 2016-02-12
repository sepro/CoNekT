from flask import Blueprint, render_template, abort

# Dict containing all keywords and the template with the information
__TOPICS = {"gene_family": "modals/help/gene_family.html",
            "interpro_domain": "modals/help/interpro_domain.html",
            "go": "modals/help/go.html",
            "correction": "modals/help/fdr.html",
            "fdr": "modals/help/fdr.html",
            "ecc": "modals/help/ecc.html"}

help = Blueprint('help', __name__)


@help.route('/<topic>')
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

