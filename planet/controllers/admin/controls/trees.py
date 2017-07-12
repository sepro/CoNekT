import os
from tempfile import mkstemp

from flask import request, flash, url_for
from planet.extensions import admin_required
from werkzeug.exceptions import abort
from werkzeug.utils import redirect

import newick

from planet import db

from planet.controllers.admin.controls import admin_controls
from planet.forms.admin.add_trees import AddTreesForm
from planet.forms.admin.reconcile_trees import ReconcileTreesForm
from planet.models.trees import TreeMethod
from planet.models.trees import Tree
from planet.models.gene_families import GeneFamily


def __read_sequence_ids(data):
    """
    Reads SequenceIDs.txt (file included in OrthoFinder Output) and parses it to a dict

    :param data: list of lines in SequenceIDs.txt
    :return: dict with key: OrthoFinder ID en value: the proper name
    """
    output = {}

    for l in data:
        if l.strip() != '':
            k, v = l.split(': ')
            output[k] = v

    return output


def __replace_ids(tree_string, conversion_table):
    """
    Replaces identifiers in a newick string with those defined in the conversion table

    :param tree_string: tree in newick format
    :param conversion_table: dict with name conversion
    :return: parsed tree, in newick format
    """
    tree = newick.loads(tree_string.strip(), strip_comments=True)[0]

    # Remove internal names, and need to be replaced with proper reconciliation.
    tree.remove_internal_names()

    for leaf in tree.get_leaves():
        if leaf.name in conversion_table.keys():
            leaf.name = conversion_table[leaf.name]

    return newick.dumps([tree])


@admin_controls.route('/reconcile/trees/', methods=['POST'])
@admin_required
def reconcile_trees():
    if request.method == 'POST':
        method_id = int(request.form.get('tree_method_id'))

        tree_method = TreeMethod.query.get_or_404(method_id)

        tree_method.reconcile_trees()

        flash('Reconciled Trees for method %d' % method_id, 'success')
        return redirect(url_for('admin.index'))


@admin_controls.route('/add/trees', methods=['POST'])
@admin_required
def add_trees():
    form = AddTreesForm(request.form)

    if request.method == 'POST':
        # First Add Method
        new_method = TreeMethod()

        new_method.description = request.form.get('description')
        new_method.gene_family_method_id = request.form.get('gene_family_method_id')

        db.session.add(new_method)

        try:
            # Commit to DB remainder
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            flash('Failed to add TreeMethod to the DB!', 'danger')
            return redirect(url_for('admin.index'))

        # Build conversion table from SequenceIDs.txt
        sequence_ids_data = request.files[form.sequence_ids.name].read().decode('utf-8')
        id_conversion = __read_sequence_ids(sequence_ids_data.split('\n'))

        # Get original gene family names (used to link trees to families
        gfs = GeneFamily.query.filter(GeneFamily.method_id == new_method.gene_family_method_id).all()
        ori_name_to_id = {gf.original_name: gf.id for gf in gfs}
        uploaded_files = request.files.getlist("tree_directory")

        new_trees = []
        for f in uploaded_files:
            # remove path from f.filename
            _, filename = os.path.split(f.filename)

            if "_tree_id.txt" not in filename:
                # not a file we need, skip
                print("Skipping %s" % filename)
                continue

            # get the gene families original name from the filename
            original_name = str(filename.split('_')[0])
            gf_id = None

            if original_name in ori_name_to_id.keys():
                gf_id = ori_name_to_id[original_name]
            else:
                print('%s: Family %s not found in gene families generated using method %d !' %
                      (f.filename, original_name, new_method.gene_family_method_id))

            tree_string = f.read().decode('utf-8').strip()

            new_trees.append({
                "gf_id": gf_id,
                "label": original_name + "_tree",
                "method_id": new_method.id,
                "data_newick": __replace_ids(tree_string, id_conversion),
                "data_phyloxml": None
            })

            # add 400 trees at the time, more can cause problems with some database engines
            if len(new_trees) > 400:
                db.engine.execute(Tree.__table__.insert(), new_trees)
                new_trees = []

        # add the last set of trees
        db.engine.execute(Tree.__table__.insert(), new_trees)

        flash('Added trees to DB.', 'success')
        return redirect(url_for('admin.index'))
    else:
        if not form.validate():
            flash('Unable to validate data, potentially missing fields', 'danger')
            return redirect(url_for('admin.index'))
        else:
            abort(405)
