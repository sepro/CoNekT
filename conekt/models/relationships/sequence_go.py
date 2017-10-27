from conekt import db

import json


class SequenceGOAssociation(db.Model):
    __tablename__ = 'sequence_go'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    sequence_id = db.Column(db.Integer, db.ForeignKey('sequences.id', ondelete='CASCADE'))
    go_id = db.Column(db.Integer, db.ForeignKey('go.id', ondelete='CASCADE'))

    evidence = db.Column(db.Enum('EXP', 'IDA', 'IPI', 'IMP', 'IGI', 'IEP',
                                 'ISS', 'ISO', 'ISA', 'ISM', 'IGC', 'IBA', 'IBD', 'IKR', 'IRD', 'RCA',
                                 'TAS', 'NAS', 'IC', 'ND', 'IEA', name='evidence'))
    source = db.Column(db.Text)

    predicted = db.Column(db.SmallInteger, default=False)
    prediction_data = db.Column(db.Text)

    sequence = db.relationship('Sequence', backref=db.backref('go_associations',
                                                              lazy='dynamic',
                                                              passive_deletes=True), lazy='joined')

    go = db.relationship('GO', backref=db.backref('sequence_associations',
                                                  lazy='dynamic',
                                                  passive_deletes=True), lazy='joined')

    def __init__(self, sequence_id, go_id, evidence, source, predicted=False, prediction_data=None):
        self.sequence_id = sequence_id
        self.go_id = go_id
        self.evidence = evidence
        self.source = source
        self.predicted = predicted
        self.prediction_data = prediction_data

    @property
    def data(self):
        """
        Property to get the information in the prediction_data as a dict. Useful for showing these values in e.g. jinja2
        templates

        :return: de-serialized prediction_data (json)
        """
        return json.loads(self.prediction_data)
