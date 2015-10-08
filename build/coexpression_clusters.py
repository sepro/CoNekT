from build.parser.planet.expression_clusters import Parser
from planet import db
from planet.models.expression_networks import ExpressionNetworkMethod
from planet.models.sequences import Sequence
from planet.models.coexpression_clusters import CoexpressionCluster, CoexpressionClusteringMethod
from planet.models.relationships import SequenceCoexpressionClusterAssociation


def add_planet_coexpression_clusters(hrr_file, hcca_file, description, network):

    # check if network exists
    network_method = ExpressionNetworkMethod.query.get(network)
    if network_method is None:
        print("ERROR: network not found.")
        quit()

    # get all sequences from the database and create a dictionary
    sequences = Sequence.query.all()

    sequence_dict = {}
    for member in sequences:
        sequence_dict[member.name.upper()] = member

    # add coexpression clustering method to the database
    clustering_method = CoexpressionClusteringMethod()

    clustering_method.network_method_id = network_method.id
    clustering_method.method = description

    try:
        db.session.add(clustering_method)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(e)
        quit()

    cluster_parser = Parser()
    cluster_parser.read_expression_clusters(hrr_file, hcca_file)

    added_clusters = {}

    for cluster_id, cluster in cluster_parser.clusters.items():
        if not cluster_id == "sNA":
            new_cluster = CoexpressionCluster()
            new_cluster.method_id = clustering_method.id
            new_cluster.name = cluster_id
            added_clusters[cluster_id] = new_cluster
            db.session.add(new_cluster)

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(e)
        quit()

    for cluster_id, cluster in cluster_parser.clusters.items():
        if not cluster_id == "sNA":
            current_cluster = added_clusters[cluster_id]

            for member in cluster:
                new_association = SequenceCoexpressionClusterAssociation()
                new_association.probe = member['probe']
                new_association.sequence_id = None
                if member['gene'].upper() in sequence_dict.keys():
                    new_association.sequence_id = sequence_dict[member['gene'].upper()].id
                new_association.coexpression_cluster_id = current_cluster.id
                db.session.add(new_association)

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(e)
