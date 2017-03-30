from flask import Blueprint, render_template, g, make_response, Response, Markup

from planet import db, cache
from planet.models.trees import TreeMethod, Tree

import json

tree = Blueprint('tree', __name__)


@tree.route('/')
@cache.cached()
def trees_overview():
    methods = TreeMethod.query.all()

    return json.dumps([m.description for m in methods])


@tree.route('/view/<int:tree_id>')
@cache.cached()
def trees_view(tree_id):
    tree = Tree.query.get_or_404(tree_id)

    return json.dumps(tree)
