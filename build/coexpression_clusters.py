from build.parser.planet.expression_clusters import Parser
from planet import db
from planet.models.species import Species
from planet.models.sequences import Sequence
from planet.models.coexpression_clusters import CoexpressionCluster, CoexpressionClusteringMethod
from planet.models.relationships import SequenceCoexpressionClusterAssociation


def add_from_planet(hrr_file, hcca_file, description, species):

    # check if species exists
    species = Species.query.filter_by(code=species).first()
    if species is None:
        print("ERROR: species", species, "not found.")
        quit()



    cluster_parser = Parser()
    cluster_parser.read_expression_clusters(hrr_file, hcca_file)

