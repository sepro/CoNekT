from planet import db
from planet.models.sequences import Sequence
from planet.models.clades import Clade

import utils.phylo as phylo

import newick
import json

SQL_COLLATION = 'NOCASE' if db.engine.name == 'sqlite' else ''


class TreeMethod(db.Model):
    __tablename__ = 'tree_methods'
    id = db.Column(db.Integer, primary_key=True)

    description = db.Column(db.Text)

    gene_family_method_id = db.Column(db.Integer,
                                      db.ForeignKey('gene_family_methods.id', ondelete='CASCADE'), index=True)

    trees = db.relationship('Tree',
                            backref=db.backref('method', lazy='joined'),
                            lazy='dynamic',
                            cascade="all, delete-orphan",
                            passive_deletes=True)

    def reconcile_trees(self):
        # Fetch required data from the database
        sequences = Sequence.query.all()
        clades = Clade.query.all()

        seq_to_species = {s.name: s.species.code for s in sequences}
        clade_to_species = {c.name: json.loads(c.species) for c in clades}

        for t in self.trees:
            # Load tree from Newick string and start reconciliating
            tree = newick.loads(t.data_newick)[0]

            for node in tree.walk():
                if len(node.descendants) != 2:
                    if not node.is_binary:
                        # Print warning in case there is a non-binary node
                        print("[%d, %s] Skipping node... Can only reconcile binary nodes ..." % (tree.id, tree.label))
                    # Otherwise it is a leaf node and can be skipped
                    continue

                branch_one_seq = [l.name for l in node.descendants[0].get_leaves()]
                branch_two_seq = [l.name for l in node.descendants[1].get_leaves()]

                branch_one_species = set([seq_to_species[s] for s in branch_one_seq if s in seq_to_species.keys()])
                branch_two_species = set([seq_to_species[s] for s in branch_two_seq if s in seq_to_species.keys()])

                all_species = branch_one_species.union(branch_two_species)

                c, s = phylo.get_clade(all_species, clade_to_species)
                duplication = phylo.is_duplication(branch_one_species, branch_two_species, clade_to_species)

                if c is not None:
                    node.name = "%s_%s" % (c, "D" if duplication else "S")

            print(newick.dumps([tree]))


class Tree(db.Model):
    __tablename__ = 'trees'
    id = db.Column(db.Integer, primary_key=True)

    label = db.Column(db.String(50, collation=SQL_COLLATION), index=True)
    data_newick = db.Column(db.Text)
    data_phyloxml = db.Column(db.Text)

    gf_id = db.Column(db.Integer, db.ForeignKey('gene_families.id', ondelete='CASCADE'), index=True)
    method_id = db.Column(db.Integer, db.ForeignKey('tree_methods.id', ondelete='CASCADE'), index=True)

    @property
    def ascii_art(self):
        """
        Returns an ascii representation of the tree. Useful for quick visualizations

        :return: string with ascii representation of the tree
        """
        tree = newick.loads(self.data_newick)[0]

        return tree.ascii_art()

    @property
    def count(self):
        tree = newick.loads(self.data_newick)[0]
        return len(tree.get_leaves())

    @property
    def sequences(self):
        tree = newick.loads(self.data_newick)[0]
        sequences = [l.name for l in tree.get_leaves()]

        return Sequence.query.filter(Sequence.name.in_(sequences))

    @property
    def tree_stripped(self):
        tree = newick.loads(self.data_newick)[0]
        tree.remove_lengths()

        print(newick.dumps([tree]))

        return newick.dumps([tree])
