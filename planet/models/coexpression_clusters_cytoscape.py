from flask import url_for
from sqlalchemy import and_

from planet.models.coexpression_clusters import CoexpressionCluster
from planet.models.relationships import SequenceFamilyAssociation

from utils.color import string_to_hex_color, string_to_shape
from utils.benchmark import benchmark

import json
from copy import deepcopy


class CoexpressionClusterCytoscape(CoexpressionCluster):

    @staticmethod
    @benchmark
    def get_cluster(cluster_id):

        cluster = super(CoexpressionClusterCytoscape, CoexpressionClusterCytoscape).get_cluster(cluster_id)

        return cluster

