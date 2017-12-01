from conekt import db


class SequenceSequenceCladeAssociation(db.Model):
    __tablename__ = 'sequence_sequence_clade'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)

    sequence_one_id = db.Column(db.Integer, db.ForeignKey('sequences.id', ondelete='CASCADE'))
    sequence_two_id = db.Column(db.Integer, db.ForeignKey('sequences.id', ondelete='CASCADE'))

    clade_id = db.Column(db.Integer, db.ForeignKey('clades.id', ondelete='CASCADE'), index=True)
    tree_id = db.Column(db.Integer, db.ForeignKey('trees.id', ondelete='CASCADE'), index=True)

    duplication = db.Column(db.SmallInteger)
    duplication_consistency_score = db.Column(db.Float)

    tree = db.relationship('Tree', lazy='joined',
                           backref=db.backref('sequence_sequence_clade_associations',
                                              lazy='dynamic',
                                              passive_deletes=True)
                           )

    clade = db.relationship('Clade', lazy='joined',
                            backref=db.backref('sequence_sequence_clade_associations',
                                               lazy='dynamic',
                                               passive_deletes=True)
                            )

    def __str__(self):
        return "%d" % self.id

    @property
    def readable_type(self):
        """
        Returns type (duplication or speciation) in a human-readable format

        :return: string Duplication or Speciation
        """
        return "Duplication" if self.duplication else "Speciation"

    @property
    def readable_score(self):
        """
        Returns the duplication consistency score in a nicer format

        :return: string with dup. consistency score in .%3 - format. Or "Not available" for speciations.
        """
        return "%.3f" % self.duplication_consistency_score if self.duplication else "Not available"