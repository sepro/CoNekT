from planet import db


class ExpressionNetworkMethod(db.Model):
    __tablename__ = 'expression_network_methods'
    id = db.Column(db.Integer, primary_key=True)
    species_id = db.Column(db.Integer, db.ForeignKey('species.id'))
    description = db.Column(db.Text)
    edge_type = db.Column(db.Enum("rank", "weight", name='edge_type'))

    probes = db.relationship('ExpressionNetwork', backref='method', lazy='dynamic')

    def __init__(self, species_id, description, edge_type="rank"):
        self.species_id = species_id
        self.description = description
        self.edge_type = edge_type


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
