from conekt import db

import json

SQL_COLLATION = 'NOCASE' if db.engine.name == 'sqlite' else ''


class ConditionTissue(db.Model):
    __tablename__ = 'conditions_tissue'
    id = db.Column(db.Integer, primary_key=True)
    species_id = db.Column(db.Integer, db.ForeignKey('species.id', ondelete='CASCADE'))
    data = db.Column(db.Text)
    description = db.Column(db.Text)

    expression_specificity_method_id = db.Column(db.Integer,
                                                 db.ForeignKey('expression_specificity_method.id', ondelete='CASCADE'),
                                                 index=True)

    in_tree = db.Column(db.SmallInteger, default=0)

    @staticmethod
    def add(species_id, data, order, colors, expression_specificity_method_id, description=''):
        """
        Add conversion table to the database for a species

        :param species_id: internal id for the species
        :param data: dict with the conversion (key = condition, value = more general feature (e.g. tissue))
        :param order: list with order of the samples in the plot
        :param colors: list with colors to use in the plot
        :param expression_specificity_method_id: ID for expression specificity method
        """
        new_ct = ConditionTissue()

        new_ct.species_id = species_id
        new_ct.data = json.dumps({'order': order,
                                  'colors': colors,
                                  'conversion': data})

        new_ct.expression_specificity_method_id = expression_specificity_method_id

        new_ct.description = description

        db.session.add(new_ct)
        db.session.commit()
