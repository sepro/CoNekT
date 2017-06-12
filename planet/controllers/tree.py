from flask import Blueprint, render_template, g, make_response, Response, Markup

from planet import db, cache
from planet.models.trees import TreeMethod, Tree
from planet.models.sequences import Sequence

from sqlalchemy.orm import joinedload

tree = Blueprint('tree', __name__)


@tree.route('/')
@cache.cached()
def trees_overview():
    methods = TreeMethod.query.all()

    return render_template('tree.html', trees=methods)


@tree.route('/view/<int:tree_id>')
@cache.cached()
def trees_view(tree_id):
    tree = Tree.query.get_or_404(tree_id)

    return render_template('tree.html', tree=tree)


@tree.route('/sequences/<tree_id>/')
@tree.route('/sequences/<tree_id>/<int:page>')
@cache.cached()
def tree_sequences(tree_id, page=1):
    """
    Returns a table with sequences with the selected interpro domain

    :param interpro_id: Internal ID of the interpro domain
    :param page: Page number
    """
    sequences = Tree.query.get(tree_id).sequences.group_by(Sequence.id)\
        .options(joinedload('species'))\
        .paginate(page, g.page_items, False).items

    return render_template('pagination/sequences.html', sequences=sequences)


@tree.route('/sequences/table/<tree_id>')
@cache.cached()
def tree_sequences_table(tree_id):
    """
    Returns a csv table with all sequences with the selected interpro domain

    :param interpro_id: Internal ID of the interpro domain
    """
    sequences = Tree.query.get(tree_id).sequences.group_by(Sequence.id)\
        .options(joinedload('species'))\
        .order_by(Sequence.name)

    return Response(render_template('tables/sequences.csv', sequences=sequences), mimetype='text/plain')


@tree.route('/newick/<tree_id>')
@cache.cached()
def newick(tree_id):
    tree = Tree.query.get_or_404(tree_id)

    response = make_response(tree.data_newick)
    response.headers["Content-Disposition"] = ("attachment; filename=" + tree.label + ".newick")
    response.headers['Content-type'] = 'text/plain'

    return response


@tree.route('/newick_no_branch_lengths/<tree_id>')
@cache.cached()
def newick_no_branch_lengths(tree_id):
    tree = Tree.query.get_or_404(tree_id)

    response = make_response(tree.tree_stripped)
    response.headers["Content-Disposition"] = ("attachment; filename=" + tree.label + ".no_branch_lengths.newick")
    response.headers['Content-type'] = 'text/plain'

    return response