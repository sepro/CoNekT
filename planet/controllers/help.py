from flask import Blueprint, render_template, abort

__TOPICS = {"gene_family": "modals/help/gene_family.html",
            "interpro_domain": "modals/help/interpro_domain.html",
            "go": "modals/help/go.html"}

help = Blueprint('help', __name__)


@help.route('/<topic>')
def help_topic(topic):
    if topic in __TOPICS.keys():
        return render_template(__TOPICS[topic])
    else:
        abort(404)

