from planet import db


class ExpressionNetworkMethod(db.Model):
    __tablename__ = 'expression_network_methods'
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.Text)

    probes = db.relationship('ExpressionNetwork', backref='method', lazy='dynamic')

    def __init__(self, description):
        self.description = description


class ExpressionNetwork(db.Model):
    __tablename__ = 'expression_networks'
    id = db.Column(db.Integer, primary_key=True)
    probe = db.Column(db.String(50))
    gene_id = db.Column(db.String(50), db.ForeignKey('sequences.id'))
    network = db.Column(db.Text)
    method_id = db.Column(db.Integer, db.ForeignKey('expression_network_methods.id'))

    def __init__(self, probe, gene_id, network, method_id):
        self.probe = probe
        self.gene_id = gene_id
        self.network = network
        self.method_id = method_id
