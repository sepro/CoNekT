from build.parser.planet.expression_clusters import Parser
from planet import db
from planet.models.expression_networks import ExpressionNetworkMethod
from planet.models.sequences import Sequence
from planet.models.coexpression_clusters import CoexpressionCluster, CoexpressionClusteringMethod
from planet.models.relationships import SequenceCoexpressionClusterAssociation


def add_planet_coexpression_clusters(hrr_file, hcca_file, description, network):

    # check if network exists
    network = ExpressionNetworkMethod.query.get(network).first()
    if network is None:
        print("ERROR: network not found.")
        quit()



    cluster_parser = Parser()
    cluster_parser.read_expression_clusters(hrr_file, hcca_file)

