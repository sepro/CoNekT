import os
import tarfile
from tempfile import mkstemp

from flask import request, flash, url_for
from conekt.extensions import admin_required
from werkzeug.exceptions import abort
from werkzeug.utils import redirect

import newick

from conekt import db

from conekt.controllers.admin.controls import admin_controls
from conekt.forms.admin.add_trees import AddTreesForm, AddGeneralTreesForm
from conekt.forms.admin.reconcile_trees import ReconcileTreesForm
from conekt.models.trees import TreeMethod
from conekt.models.trees import Tree
from conekt.models.gene_families import GeneFamily


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

        # Get original gene family names (used to link trees to families)
        gfs = GeneFamily.query.filter(GeneFamily.method_id == new_method.gene_family_method_id).all()
        ori_name_to_id = {gf.original_name: gf.id for gf in gfs}
        tree_data = request.files[form.tree_archive.name].read()

        fd, temp_path = mkstemp()

        with open(temp_path, 'wb') as tree_data_writer:
            tree_data_writer.write(tree_data)

        new_trees = []
        with tarfile.open(temp_path, mode='r:gz') as tf:
            for name, entry in zip(tf.getnames(), tf):
                tree_string = str(tf.extractfile(entry).read().decode('utf-8')).replace('\r', '').replace('\n','')

                # get the gene families original name from the filename
                original_name = str(name.split('_')[0])
                gf_id = None

                if original_name in ori_name_to_id.keys():
                    gf_id = ori_name_to_id[original_name]
                else:
                    print('%s: Family %s not found in gene families generated using method %d !' %
                          (name, original_name, new_method.gene_family_method_id))

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


@admin_controls.route('/add/general_trees', methods=['POST'])
@admin_required
def add_trees_general():
    form = AddGeneralTreesForm(request.form)

    if request.method == 'POST':
        new_method = TreeMethod()

        new_method.description = request.form.get('description')
        new_method.gene_family_method_id = request.form.get('gene_family_method_id')

        db.session.add(new_method)

        try:
            # Commit to DB remainder
            db.session.commit()
        except Exception as _:
            db.session.rollback()
            flash('Failed to add TreeMethod to the DB!', 'danger')
            return redirect(url_for('admin.index'))

        # Get original gene family names (used to link trees to families)
        gfs = GeneFamily.query.filter(GeneFamily.method_id == new_method.gene_family_method_id).all()
        name_to_id = {gf.name: gf.id for gf in gfs}
        tree_data = request.files[form.general_tree_archive.name].read()

        fd, temp_path = mkstemp()

        with open(temp_path, 'wb') as tree_data_writer:
            tree_data_writer.write(tree_data)

        new_trees = []
        with tarfile.open(temp_path, mode='r:gz') as tf:
            for name, entry in zip(tf.getnames(), tf):
                tree_string = str(tf.extractfile(entry).read().decode('utf-8')).replace('\r', '').replace('\n', '')

                # get the gene families original name from the filename
                current_tree_name = str(name.split('.')[0])
                gf_id = None

                if current_tree_name in name_to_id.keys():
                    gf_id = name_to_id[current_tree_name]
                else:
                    print(
                        '%s: Family %s not found in gene families generated using method %d !' %
                        (name, current_tree_name, new_method.gene_family_method_id)
                    )

                tree = newick.loads(tree_string)[0]

                new_trees.append({
                    "gf_id": gf_id,
                    "label": current_tree_name + "_tree",
                    "method_id": new_method.id,
                    "data_newick": tree_string,
                    "data_phyloxml": newick.dumps([tree])
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