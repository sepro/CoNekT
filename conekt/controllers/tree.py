from flask import Blueprint, render_template, g, make_response, Response, Markup

from conekt import db, cache
from conekt.models.trees import TreeMethod, Tree
from conekt.models.sequences import Sequence
from conekt.models.relationships.sequence_sequence_clade import SequenceSequenceCladeAssociation

from sqlalchemy.orm import joinedload

tree = Blueprint('tree', __name__)


@tree.route('/')
@cache.cached()
def trees_overview():
    methods = TreeMethod.query.all()

    return render_template('tree.html', trees=methods)


@tree.route('/view/<int:tree_id>')
@cache.cached()
def tree_view(tree_id):
    tree = Tree.query.get_or_404(tree_id)
    association_count = SequenceSequenceCladeAssociation.query.filter(SequenceSequenceCladeAssociation.tree_id ==tree_id).count()

    return render_template('tree.html', tree=tree, association_count=association_count)


@tree.route('/sequences/<tree_id>/')
@tree.route('/sequences/<tree_id>/<int:page>')
@cache.cached()
def tree_sequences(tree_id, page=1):
    """
    Returns a paginated table with sequences from the selected tree

    :param tree_id: Internal ID of the desired tree
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
    Returns a csv table with all sequences from the selected tree

    :param tree_id: Internal ID of the desired tree
    """
    sequences = Tree.query.get(tree_id).sequences.group_by(Sequence.id)\
        .options(joinedload('species'))\
        .order_by(Sequence.name).all()

    return Response(render_template('tables/sequences.csv', sequences=sequences), mimetype='text/plain')


@tree.route('/associations/<tree_id>/')
@tree.route('/associations/<tree_id>/<int:page>')
@cache.cached()
def tree_associations(tree_id, page=1):
    relations = SequenceSequenceCladeAssociation.query.filter(SequenceSequenceCladeAssociation.tree_id == tree_id).\
        paginate(page, g.page_items, False).items

    return render_template('pagination/clade_relations.html', relations=relations)


@tree.route('/associations/table/<tree_id>/')
@cache.cached()
def tree_associations_table(tree_id):
    relations = SequenceSequenceCladeAssociation.query.filter(SequenceSequenceCladeAssociation.tree_id ==tree_id).all()

    return Response(render_template('tables/clade_associations.csv', relations=relations), mimetype='text/plain')


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


@tree.route('/ascii/<tree_id>')
@cache.cached()
def ascii_tree(tree_id):
    tree = Tree.query.get_or_404(tree_id)

    response = make_response(tree.ascii_art)
    response.headers["Content-Disposition"] = ("attachment; filename=" + tree.label + ".ascii.txt")
    response.headers['Content-type'] = 'text/plain'

    return response


@tree.route('/phyloxml/<tree_id>.xml')
@cache.cached()
def phyloxml(tree_id):
    tree = Tree.query.get_or_404(tree_id)

    response = make_response(tree.phyloxml)
    response.headers["Content-Disposition"] = ("attachment; filename=" + tree.label + ".xml")
    response.headers['Content-type'] = 'application/xml'

    return response
