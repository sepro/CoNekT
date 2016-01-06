#!/usr/bin/env python3
from planet import create_app, db

from planet.models.users import User
from planet.models.expression_profiles import ExpressionProfile
from planet.models.sequences import Sequence
from planet.models.species import Species
from planet.models.interpro import Interpro
from planet.models.go import GO
from planet.models.gene_families import GeneFamily, GeneFamilyMethod
from planet.models.coexpression_clusters import CoexpressionCluster, CoexpressionClusteringMethod
from planet.models.expression_networks import ExpressionNetwork, ExpressionNetworkMethod
from planet.models.relationships import SequenceCoexpressionClusterAssociation
from planet.models.clades import Clade

from planet.controllers.help import __TOPICS as topics

from flask.ext.testing import TestCase

from tests.config import LOGIN_ENABLED, BLAST_ENABLED

import sys
import json
import unittest


class WebsiteTest(TestCase):
    """
    TestCase to check if the website is functional
        * a DB will be created and filled with dummy data
        * an app will be spawned with the testing config, DO NOT run this against a database that is in use !!
        * the DB will be cleared !
    """

    def create_app(self):
        """
        Creates the app using the tests config (tests/config.py)

        :return: flask app with settings from tests/config.py
        """
        app = create_app('tests.config')
        return app

    def setUp(self):
        """
        Creates a database and fills it with sufficient dummy data to run the tests.
        """
        db.create_all()

        test_user = User('admin', 'admin', '', is_admin=True)

        test_species = Species('tst', 'Unittest species')
        test_interpro = Interpro('IPR_TEST', 'Test label')
        test_go = GO('GO:TEST', 'test_process', 'biological_process',  'Test label', False, None, None)
        test_go2 = GO('GO:TEST2', 'test2', 'biological_process',  'Test', False, None, None)

        test_gf_method = GeneFamilyMethod('test_gf_method')
        test_gf = GeneFamily('test_gf')

        db.session.add(test_user)
        db.session.add(test_species)
        db.session.add(test_interpro)
        db.session.add(test_go)
        db.session.add(test_go2)
        db.session.add(test_gf_method)
        db.session.add(test_gf)
        db.session.commit()

        test_gf.method_id = test_gf_method.id

        db.session.commit()

        test_sequence = Sequence(test_species.id, 'TEST_SEQ_01', 'ATG', description='test sequence')
        test_sequence.families.append(test_gf)
        test_sequence.interpro_domains.append(test_interpro)
        test_sequence.go_labels.append(test_go)

        test_sequence2 = Sequence(test_species.id, 'TEST_SEQ_02', 'ATG', description='test sequence')

        db.session.add(test_sequence)
        db.session.add(test_sequence2)
        db.session.commit()

        test_profile = ExpressionProfile('test_probe', test_sequence.id, '{"data": {"seedling - hypocotyl 17d": [29.0, 44.0, 35.0], "stage 15 flower - pedicel +21d": [39.0, 18.0, 28.0], "senescing leaf 35d": [104.0, 95.0, 121.0], "stage 12 flower - stamen +21d": [56.0, 41.0, 40.0], "seed - triangle stage 56d": [18.0, 21.0, 37.0], "pollen - uninuclear stage": [17.0, 17.0], "seed - globular stage 56d": [17.0, 28.0, 25.0], "root 21d": [49.0, 46.0, 49.0], "stage 12 flower - carpel +21d": [29.0, 34.0, 38.0], "quiescent center and endodermis, beyond the mature hair zone": [5.0, 5.0, 17.0], "stage 12 flower +21d": [26.0, 39.0, 41.0], "mature seed 56d": [14.0, 12.0, 11.0], "shoot 21d": [94.0, 63.0, 75.0], "stage 10 flower +21d": [83.0, 112.0, 99.0], "stage 12 flower - petal +21d": [68.0, 57.0, 47.0], "seed - heart stage 56d": [44.0, 39.0, 17.0], "stage 1 flower 21d": [126.0, 120.0, 116.0], "stem 2nd internode +21d": [41.0, 42.0, 41.0], "pollen stage 10 - pollen sac  42d": [22.0, 46.0, 31.0], "endodermis, cortex and quiescent center": [13.0, 20.0, 13.0], "rosette leaf 10d": [40.0, 27.0, 44.0], "root 17d": [44.0, 53.0, 51.0], "stage 12 flower - sepal +21d": [56.0, 39.0, 53.0], "stage 9 flower +21d": [113.0, 107.0, 143.0], "~0.15 mm from the root tip": [58.0, 35.0, 17.0, 15.0], "stage 15 flower - carpel +21d": [33.0, 22.0, 24.0], "~0.30 mm from the root tip": [13.0, 13.0, 24.0, 66.0], "rosette leaf - distal half 17d": [18.0, 25.0, 20.0], "petiole 17d": [28.0, 19.0, 20.0], "pollen - bicellular stage": [26.0, 16.0], "atrichoblasts from the quiescent center up": [7.0, 20.0, 8.0], "~0.45 to 2 mm from the root tip": [0.0, 23.0, 20.0, 3.0], "complete rosette 22d": [19.0, 29.0, 24.0], "pollen - tricellular stage": [22.0, 32.0], "stem 1st internode +21d": [72.0, 78.0, 63.0], "stage 15 flower +21d": [32.0, 38.0, 39.0], "pollen - mature": [31.0, 46.0, 22.0], "cauline leaf +21d": [58.0, 41.0, 51.0], "seedling - shoot apex 7d": [27.0, 23.0, 43.0], "complete rosette 23d": [21.0, 20.0, 20.0], "seedling - rosette leaf 7d": [42.0, 40.0, 33.0], "complete rosette 21d": [21.0, 26.0, 22.0], "rosette leaf 17d": [62.0, 57.0, 29.0], "seed - torpedo stage 56d": [24.0, 32.0, 23.0], "rosette leaf - proximal half 17d": [26.0, 17.0, 21.0], "seedling - cotyledon 7d": [50.0, 31.0, 25.0], "stage 15 flower - stamen +21d": [30.0, 18.0, 28.0], "root stele to elongation zone": [20.0, 9.0, 11.0], "stage 15 flower - sepal +21d": [49.0, 28.0, 22.0], "stage 15 flower - petal +21d": [30.0, 19.0, 45.0], "seed - curled cotyledon stage 56d": [16.0, 15.0, 15.0], "lateral root cap and epidermis": [12.0, 6.0, 5.0]}, "order": ["seedling - cotyledon 7d", "seedling - hypocotyl 17d", "seedling - rosette leaf 7d", "seedling - shoot apex 7d", "root 17d", "root 21d", "~0.15 mm from the root tip", "~0.30 mm from the root tip", "~0.45 to 2 mm from the root tip", "atrichoblasts from the quiescent center up", "endodermis, cortex and quiescent center", "lateral root cap and epidermis", "quiescent center and endodermis, beyond the mature hair zone", "root stele to elongation zone", "rosette leaf 10d", "rosette leaf 17d", "rosette leaf - distal half 17d", "rosette leaf - proximal half 17d", "complete rosette 21d", "complete rosette 22d", "complete rosette 23d", "senescing leaf 35d", "cauline leaf +21d", "petiole 17d", "shoot 21d", "stem 1st internode +21d", "stem 2nd internode +21d", "stage 1 flower 21d", "stage 9 flower +21d", "stage 10 flower +21d", "stage 12 flower - carpel +21d", "stage 12 flower - petal +21d", "stage 12 flower - sepal +21d", "stage 12 flower - stamen +21d", "stage 12 flower +21d", "stage 15 flower - carpel +21d", "stage 15 flower - pedicel +21d", "stage 15 flower - petal +21d", "stage 15 flower - sepal +21d", "stage 15 flower - stamen +21d", "stage 15 flower +21d", "seed - curled cotyledon stage 56d", "seed - globular stage 56d", "seed - heart stage 56d", "seed - torpedo stage 56d", "seed - triangle stage 56d", "mature seed 56d", "pollen stage 10 - pollen sac  42d", "pollen - uninuclear stage", "pollen - bicellular stage", "pollen - tricellular stage", "pollen - mature"]}')
        test_profile.species_id = test_species.id
        test_profile2 = ExpressionProfile('test_probe2', test_sequence2.id, '{"data": {"seedling - hypocotyl 17d": [29.0, 44.0, 35.0], "stage 15 flower - pedicel +21d": [39.0, 18.0, 28.0], "senescing leaf 35d": [104.0, 95.0, 121.0], "stage 12 flower - stamen +21d": [56.0, 41.0, 40.0], "seed - triangle stage 56d": [18.0, 21.0, 37.0], "pollen - uninuclear stage": [17.0, 17.0], "seed - globular stage 56d": [17.0, 28.0, 25.0], "root 21d": [49.0, 46.0, 49.0], "stage 12 flower - carpel +21d": [29.0, 34.0, 38.0], "quiescent center and endodermis, beyond the mature hair zone": [5.0, 5.0, 17.0], "stage 12 flower +21d": [26.0, 39.0, 41.0], "mature seed 56d": [14.0, 12.0, 11.0], "shoot 21d": [94.0, 63.0, 75.0], "stage 10 flower +21d": [83.0, 112.0, 99.0], "stage 12 flower - petal +21d": [68.0, 57.0, 47.0], "seed - heart stage 56d": [44.0, 39.0, 17.0], "stage 1 flower 21d": [126.0, 120.0, 116.0], "stem 2nd internode +21d": [41.0, 42.0, 41.0], "pollen stage 10 - pollen sac  42d": [22.0, 46.0, 31.0], "endodermis, cortex and quiescent center": [13.0, 20.0, 13.0], "rosette leaf 10d": [40.0, 27.0, 44.0], "root 17d": [44.0, 53.0, 51.0], "stage 12 flower - sepal +21d": [56.0, 39.0, 53.0], "stage 9 flower +21d": [113.0, 107.0, 143.0], "~0.15 mm from the root tip": [58.0, 35.0, 17.0, 15.0], "stage 15 flower - carpel +21d": [33.0, 22.0, 24.0], "~0.30 mm from the root tip": [13.0, 13.0, 24.0, 66.0], "rosette leaf - distal half 17d": [18.0, 25.0, 20.0], "petiole 17d": [28.0, 19.0, 20.0], "pollen - bicellular stage": [26.0, 16.0], "atrichoblasts from the quiescent center up": [7.0, 20.0, 8.0], "~0.45 to 2 mm from the root tip": [0.0, 23.0, 20.0, 3.0], "complete rosette 22d": [19.0, 29.0, 24.0], "pollen - tricellular stage": [22.0, 32.0], "stem 1st internode +21d": [72.0, 78.0, 63.0], "stage 15 flower +21d": [32.0, 38.0, 39.0], "pollen - mature": [31.0, 46.0, 22.0], "cauline leaf +21d": [58.0, 41.0, 51.0], "seedling - shoot apex 7d": [27.0, 23.0, 43.0], "complete rosette 23d": [21.0, 20.0, 20.0], "seedling - rosette leaf 7d": [42.0, 40.0, 33.0], "complete rosette 21d": [21.0, 26.0, 22.0], "rosette leaf 17d": [62.0, 57.0, 29.0], "seed - torpedo stage 56d": [24.0, 32.0, 23.0], "rosette leaf - proximal half 17d": [26.0, 17.0, 21.0], "seedling - cotyledon 7d": [50.0, 31.0, 25.0], "stage 15 flower - stamen +21d": [30.0, 18.0, 28.0], "root stele to elongation zone": [20.0, 9.0, 11.0], "stage 15 flower - sepal +21d": [49.0, 28.0, 22.0], "stage 15 flower - petal +21d": [30.0, 19.0, 45.0], "seed - curled cotyledon stage 56d": [16.0, 15.0, 15.0], "lateral root cap and epidermis": [12.0, 6.0, 5.0]}, "order": ["seedling - cotyledon 7d", "seedling - hypocotyl 17d", "seedling - rosette leaf 7d", "seedling - shoot apex 7d", "root 17d", "root 21d", "~0.15 mm from the root tip", "~0.30 mm from the root tip", "~0.45 to 2 mm from the root tip", "atrichoblasts from the quiescent center up", "endodermis, cortex and quiescent center", "lateral root cap and epidermis", "quiescent center and endodermis, beyond the mature hair zone", "root stele to elongation zone", "rosette leaf 10d", "rosette leaf 17d", "rosette leaf - distal half 17d", "rosette leaf - proximal half 17d", "complete rosette 21d", "complete rosette 22d", "complete rosette 23d", "senescing leaf 35d", "cauline leaf +21d", "petiole 17d", "shoot 21d", "stem 1st internode +21d", "stem 2nd internode +21d", "stage 1 flower 21d", "stage 9 flower +21d", "stage 10 flower +21d", "stage 12 flower - carpel +21d", "stage 12 flower - petal +21d", "stage 12 flower - sepal +21d", "stage 12 flower - stamen +21d", "stage 12 flower +21d", "stage 15 flower - carpel +21d", "stage 15 flower - pedicel +21d", "stage 15 flower - petal +21d", "stage 15 flower - sepal +21d", "stage 15 flower - stamen +21d", "stage 15 flower +21d", "seed - curled cotyledon stage 56d", "seed - globular stage 56d", "seed - heart stage 56d", "seed - torpedo stage 56d", "seed - triangle stage 56d", "mature seed 56d", "pollen stage 10 - pollen sac  42d", "pollen - uninuclear stage", "pollen - bicellular stage", "pollen - tricellular stage", "pollen - mature"]}')
        test_profile2.species_id = test_species.id
        db.session.add(test_profile)
        db.session.add(test_profile2)
        db.session.commit()

        test_expression_network_method = ExpressionNetworkMethod(test_species.id, "Test network method")
        db.session.add(test_expression_network_method)
        db.session.commit()

        test_expression_network = ExpressionNetwork(test_profile.probe,
                                                    test_sequence.id,
                                                    '[{"gene_name": "TEST_SEQ_02", "gene_id": ' + str(test_sequence2.id)
                                                    + ', "probe_name": "test_probe2", "link_score": 0}]',
                                                    test_expression_network_method.id)

        test_expression_network2 = ExpressionNetwork(test_profile2.probe,
                                                     test_sequence2.id,
                                                     '[{"gene_name": "TEST_SEQ_01", "gene_id": ' + str(test_sequence.id)
                                                     + ', "probe_name": "test_probe2", "link_score": 0}]',
                                                     test_expression_network_method.id)

        db.session.add(test_expression_network)
        db.session.add(test_expression_network2)
        db.session.commit()

        test_expression_network_method.update_count()

        test_cluster_method = CoexpressionClusteringMethod()
        test_cluster_method.network_method_id = test_expression_network_method.id
        test_cluster_method.method = 'test clustering method'

        db.session.add(test_cluster_method)
        db.session.commit()

        test_cluster = CoexpressionCluster()
        test_cluster.method_id = test_cluster_method.id
        test_cluster.name = 'TEST_COEXP_CLUSTER'

        db.session.add(test_cluster)
        db.session.commit()

        test_cluster_method.update_counts()

        new_association = SequenceCoexpressionClusterAssociation()
        new_association.probe = test_profile.probe
        new_association.sequence_id = test_sequence.id
        new_association.coexpression_cluster_id = test_cluster.id

        new_association2 = SequenceCoexpressionClusterAssociation()
        new_association2.probe = test_profile2.probe
        new_association2.sequence_id = test_sequence2.id
        new_association2.coexpression_cluster_id = test_cluster.id

        db.session.add(new_association)
        db.session.add(new_association2)
        db.session.commit()

        Clade.add_clade('test', ["tst"])

    def tearDown(self):
        """
        Removes test database again, so the next test can start with a clean slate
        """
        db.session.remove()
        db.drop_all()

    def assertCytoscapeJson(self, data):
        self.assertTrue('nodes' in data.keys())
        self.assertTrue('edges' in data.keys())

        for node in data['nodes']:
            self.assertTrue('color' in node['data'].keys())
            self.assertTrue('id' in node['data'].keys())

            compound = node['data']['compound'] if 'compound' in node['data'].keys() else False

            if not compound:
                self.assertTrue('data' in node.keys())
                self.assertTrue('family_color' in node['data'].keys())
                self.assertTrue('lc_color' in node['data'].keys())
                self.assertTrue('lc_shape' in node['data'].keys())
                self.assertTrue('family_name' in node['data'].keys())
                self.assertTrue('shape' in node['data'].keys())
                self.assertTrue('description' in node['data'].keys())
                self.assertTrue('name' in node['data'].keys())
                self.assertTrue('gene_name' in node['data'].keys())
                self.assertTrue('tokens' in node['data'].keys())
                self.assertTrue('depth' in node['data'].keys())
                self.assertTrue('family_clade_count' in node['data'].keys())
                self.assertTrue('gene_id' in node['data'].keys())
                self.assertTrue('family_id' in node['data'].keys())
                self.assertTrue('family_clade' in node['data'].keys())
                self.assertTrue('family_shape' in node['data'].keys())
                self.assertTrue('profile_link' in node['data'].keys())

        for edge in data['edges']:
            self.assertTrue('data' in edge.keys())
            self.assertTrue('source' in edge['data'].keys())
            self.assertTrue('target' in edge['data'].keys())
            self.assertTrue('color' in edge['data'].keys())

            homology = edge['data']['homology'] if 'homology' in edge['data'].keys() else False

            if not homology:
                self.assertTrue('link_score' in edge['data'].keys())
                self.assertTrue('profile_comparison' in edge['data'].keys())
                self.assertTrue('edge_type' in edge['data'].keys())
                self.assertTrue('depth' in edge['data'].keys())

    def test_sequence(self):
        """
        Test for routes associated with a Sequence
        """
        sequence = Sequence.query.first()
        if sequence is not None:
            response = self.client.get("/sequence/view/%d" % sequence.id)
            self.assert_template_used('sequence.html')
            self.assert200(response)

            response = self.client.get("/sequence/fasta/coding/%d" % sequence.id)
            self.assert200(response)
            data = response.data.decode("utf-8").strip()
            self.assertEqual(len(data.split('\n')), 2)
            self.assertEqual(data[0], '>')
            self.assertTrue('>' + sequence.name + '\n' in data)

            response = self.client.get("/sequence/fasta/protein/%d" % sequence.id)
            self.assert200(response)
            data = response.data.decode("utf-8").strip()
            self.assertEqual(len(data.split('\n')), 2)
            self.assertEqual(data[0], '>')
            self.assertTrue('>' + sequence.name + '\n' in data)

            response = self.client.get("/sequence/find/" + sequence.name)
            self.assert_template_used('sequence.html')
            self.assert200(response)

            response = self.client.get("/sequence/view/a")
            self.assert404(response)
        else:
            print('  * test_sequence: No sequence found, skipping test...', file=sys.stderr)

    def test_species(self):
        """
        Test for routes associated with a Species
        """
        response = self.client.get("/species/")
        self.assert_template_used('species.html')
        self.assert200(response)

        species = Species.query.first()
        sequence = species.sequences.first()
        if species is not None:
            response = self.client.get("/species/view/%d" % species.id)
            self.assert_template_used('species.html')
            self.assert200(response)

            response = self.client.get("/species/sequences/%d/1" % species.id)
            self.assert_template_used('pagination/sequences.html')
            self.assert200(response)

            response = self.client.get("/species/download/coding/%d" % species.id)
            self.assert200(response)
            data = response.data.decode("utf-8").strip()
            self.assertTrue(len(data.split('\n')) > 0)
            self.assertEqual(data[0], '>')
            self.assertTrue('>' + sequence.name + '\n' in data)

            response = self.client.get("/species/download/protein/%d" % species.id)
            self.assert200(response)
            data = response.data.decode("utf-8").strip()
            self.assertTrue(len(data.split('\n')) > 0)
            self.assertEqual(data[0], '>')
            self.assertTrue('>' + sequence.name + '\n' in data)

            response = self.client.get("/species/stream/coding/%d" % species.id)
            self.assert200(response)
            data = response.data.decode("utf-8").strip()
            self.assertTrue(len(data.split('\n')) > 0)
            self.assertEqual(data[0], '>')
            self.assertTrue('>' + sequence.name + '\n' in data)

            response = self.client.get("/species/stream/protein/%d" % species.id)
            self.assert200(response)
            data = response.data.decode("utf-8").strip()
            self.assertTrue(len(data.split('\n')) > 0)
            self.assertEqual(data[0], '>')
            self.assertTrue('>' + sequence.name + '\n' in data)
        else:
            print('  * test_species: No species found, skipping test...', file=sys.stderr)

    def test_interpro(self):
        """
        Test for routes associated with an InterPro domain
        """
        interpro = Interpro.query.first()
        if interpro is not None:
            response = self.client.get("/interpro/view/%d" % interpro.id)
            self.assert_template_used('interpro.html')
            self.assert200(response)

            response = self.client.get("/interpro/find/" + interpro.label)
            self.assert_template_used('interpro.html')
            self.assert200(response)

            response = self.client.get("/interpro/sequences/%d/1" % interpro.id)
            self.assert_template_used('pagination/sequences.html')
            self.assert200(response)

            response = self.client.get("/interpro/sequences/table/%d" % interpro.id)
            self.assert_template_used('tables/sequences.csv')
            self.assert200(response)

            response = self.client.get("/interpro/json/species/%d" % interpro.id)
            self.assert200(response)

            data = json.loads(response.data.decode('utf-8'))

            self.assertTrue('highlight' in data[0].keys())
            self.assertTrue('color' in data[0].keys())
            self.assertTrue('value' in data[0].keys())
            self.assertTrue('label' in data[0].keys())

        else:
            print('  * test_interpro: No interpro domain found, skipping test...', file=sys.stderr)

    def test_go(self):
        """
        Test for routes associated with a GO label
        """
        go = GO.query.first()

        if go is not None:
            response = self.client.get("/go/view/%d" % go.id)
            self.assert_template_used('go.html')
            self.assert200(response)

            response = self.client.get("/go/find/" + go.label)
            self.assertRedirects(response, "/go/view/%d" % go.id)

            response = self.client.get("/go/sequences/%d/1" % go.id)
            self.assert_template_used('pagination/sequences.html')
            self.assert200(response)

            response = self.client.get("/go/sequences/table/%d" % go.id)
            self.assert_template_used('tables/sequences.csv')
            self.assert200(response)

            response = self.client.get("/go/json/species/%d" % go.id)
            self.assert200(response)

            data = json.loads(response.data.decode('utf-8'))

            self.assertTrue('highlight' in data[0].keys())
            self.assertTrue('color' in data[0].keys())
            self.assertTrue('value' in data[0].keys())
            self.assertTrue('label' in data[0].keys())

            response = self.client.get("/go/json/genes/" + go.label)
            self.assert200(response)

            data = json.loads(response.data.decode('utf-8'))
            self.assertTrue(1 in data)
        else:
            print('  * test_go: No go label found, skipping test...', file=sys.stderr)

    def test_family(self):
        """
        Test for routes associated with a GeneFamily
        """
        family = GeneFamily.query.first()

        if family is not None:
            response = self.client.get("/family/view/%d" % family.id)
            self.assert_template_used('family.html')
            self.assert200(response)

            response = self.client.get("/family/find/" + family.name)
            self.assert_template_used('family.html')
            self.assert200(response)

            response = self.client.get("/family/sequences/%d/1" % family.id)
            self.assert_template_used('pagination/sequences.html')
            self.assert200(response)

            response = self.client.get("/family/sequences/table/%d" % family.id)
            self.assert_template_used('tables/sequences.csv')
            self.assert200(response)

            response = self.client.get("/family/json/species/%d" % family.id)
            self.assert200(response)

            data = json.loads(response.data.decode('utf-8'))

            self.assertTrue('highlight' in data[0].keys())
            self.assertTrue('color' in data[0].keys())
            self.assertTrue('value' in data[0].keys())
            self.assertTrue('label' in data[0].keys())
        else:
            print('  * test_family: No family found, skipping test...', file=sys.stderr)

    def test_profile(self):
        """
        Test for routes associated with an ExpressionProfile
        """
        profile = ExpressionProfile.query.first()
        if profile is not None:
            response = self.client.get("/profile/view/%d" % profile.id)
            self.assert_template_used('expression_profile.html')
            self.assert200(response)

            response = self.client.get("/profile/modal/%d" % profile.id)
            self.assert_template_used('modals/expression_profile.html')
            self.assert200(response)

            response = self.client.get("/profile/find/" + profile.probe)
            self.assert_template_used('expression_profile.html')
            self.assert200(response)

            response = self.client.get("/profile/find/%s/%d" % (profile.probe, 2))
            self.assert404(response)

            response = self.client.get("/profile/compare/%d/%d" % (profile.id, profile.id))
            self.assert_template_used('compare_profiles.html')
            self.assert200(response)

            response = self.client.get("/profile/compare_probes/%s/%s/%d" % (profile.probe, profile.probe, 1))
            self.assert_template_used('compare_profiles.html')
            self.assert200(response)

            response = self.client.get("/profile/compare_probes/%s/%s/%d" % (profile.probe, profile.probe, 2))
            self.assert404(response)

            response = self.client.get("/profile/json/radar/%d" % profile.id)
            self.assert200(response)
            data = json.loads(response.data.decode('utf-8'))
            self.assertTrue('labels' in data.keys())
            self.assertTrue('datasets' in data.keys())
            self.assertTrue('strokeColor' in data['datasets'][0].keys())
            self.assertTrue('data' in data['datasets'][0].keys())
            self.assertTrue('pointStrokeColor' in data['datasets'][0].keys())
            self.assertTrue('fillColor' in data['datasets'][0].keys())
            self.assertTrue('label' in data['datasets'][0].keys())
            self.assertTrue('pointHighlightStroke' in data['datasets'][0].keys())
            self.assertTrue('pointColor' in data['datasets'][0].keys())
            self.assertTrue('pointHighlightFill' in data['datasets'][0].keys())

            response = self.client.get("/profile/json/plot/%d" % profile.id)
            self.assert200(response)

            data = json.loads(response.data.decode('utf-8'))
            self.assertTrue('labels' in data.keys())
            self.assertTrue('datasets' in data.keys())
            for i in range(3):
                self.assertTrue('strokeColor' in data['datasets'][i].keys())
                self.assertTrue('data' in data['datasets'][i].keys())
                self.assertTrue('pointStrokeColor' in data['datasets'][i].keys())
                self.assertTrue('fillColor' in data['datasets'][i].keys())
                self.assertTrue('label' in data['datasets'][i].keys())
                self.assertTrue('pointHighlightStroke' in data['datasets'][i].keys())
                self.assertTrue('pointColor' in data['datasets'][i].keys())
                self.assertTrue('pointHighlightFill' in data['datasets'][i].keys())

            response = self.client.get("/profile/json/compare_plot/%d/%d" % (profile.id, profile.id))
            self.assert200(response)

            data = json.loads(response.data.decode('utf-8'))
            self.assertTrue('labels' in data.keys())
            self.assertTrue('datasets' in data.keys())
            for i in range(2):
                self.assertTrue('strokeColor' in data['datasets'][i].keys())
                self.assertTrue('data' in data['datasets'][i].keys())
                self.assertTrue('pointStrokeColor' in data['datasets'][i].keys())
                self.assertTrue('fillColor' in data['datasets'][i].keys())
                self.assertTrue('label' in data['datasets'][i].keys())
                self.assertTrue('pointHighlightStroke' in data['datasets'][i].keys())
                self.assertTrue('pointColor' in data['datasets'][i].keys())
                self.assertTrue('pointHighlightFill' in data['datasets'][i].keys())
        else:
            print('  * test_profile: No profile found, skipping test...', file=sys.stderr)

    def test_help(self):
        """
        Test for help pages (which are static)
        """
        for k, v in topics.items():
            response = self.client.get("/help/%s" % k)
            self.assert_template_used(v)
            self.assert200(response)

    def test_search(self):
        """
        Test different components of the search function
        """
        sequence = Sequence.query.first()
        interpro = Interpro.query.first()
        go = GO.query.first()

        response = self.client.get('/search/keyword/%s' % sequence.name)
        self.assertRedirects(response, '/sequence/view/%d' % sequence.id)

        response = self.client.get('/search/keyword/%s' % interpro.label)
        self.assertRedirects(response, '/interpro/view/%d' % interpro.id)

        response = self.client.get('/search/keyword/%s' % go.label)
        self.assertRedirects(response, '/go/view/%d' % go.id)

        response = self.client.get('/search/')
        self.assertRedirects(response, '/')

        response = self.client.post('/search/', data=dict(terms="TEST_SEQ_01"))
        self.assertRedirects(response, '/sequence/view/%d' % sequence.id)

        response = self.client.post('/search/', data=dict(terms='Test label'))
        self.assert_template_used('search_results.html')
        self.assert200(response)

        response = self.client.get('/search/json/genes/%s' % go.label)
        self.assert200(response)
        data = json.loads(response.data.decode('utf-8'))
        self.assertTrue(sequence.id in data)

        # TODO: search_enriched_clusters() is currently untested !

        response = self.client.get('/search/typeahead/go/prefetch')
        self.assert200(response)
        data = json.loads(response.data.decode('utf-8'))
        self.assertTrue(len(data) == 1)
        for d in data:
            self.assertTrue('value' in d.keys())
            self.assertTrue('tokens' in d.keys())

        response = self.client.get('/search/typeahead/go/test.json')
        self.assert200(response)
        data = json.loads(response.data.decode('utf-8'))
        self.assertTrue(len(data) == 2)
        for d in data:
            self.assertTrue('value' in d.keys())
            self.assertTrue('tokens' in d.keys())

    @unittest.skipIf(not LOGIN_ENABLED, "Skipping test because LOGIN is not enabled")
    def test_auth(self):
        """
        Test if a user can log in
        """
        response = self.client.get('/auth/login')
        self.assert_template_used('login.html')
        self.assert200(response)

        response = self.client.post('/auth/login', data=dict(username='admin', password='admin', keep_logged='y'),
                                    follow_redirects=True)
        self.assert200(response)
        self.assertTrue('You have successfully logged in.' in response.data.decode('utf-8'))

        response = self.client.get('/auth/logout', follow_redirects=True)
        self.assert200(response)
        self.assertTrue('You have successfully logged out.' in response.data.decode('utf-8'))

        response = self.client.post('/auth/login', data=dict(username='admin', password='wrong', keep_logged='y'),
                                    follow_redirects=True)
        self.assert200(response)
        self.assertTrue('Invalid username or password. Please try again.' in response.data.decode('utf-8'))

    @unittest.skipIf(not BLAST_ENABLED, "Skipping test because BLAST is not enabled")
    def test_blast(self):
        """
        Test basic components of the BLAST search

        TODO: check if BLAST is configured correctly !
        """
        response = self.client.get('/blast/')
        self.assert_template_used('blast.html')
        self.assert200(response)

        response = self.client.get('/blast/results/testtoken')
        self.assert_template_used('blast.html')
        self.assert200(response)

        response = self.client.get('/blast/results/json/testtoken')
        self.assert200(response)
        data = json.loads(response.data.decode('utf-8'))
        self.assertTrue('status' in data)

    def test_heatmap(self):
        profile = ExpressionProfile.query.first()
        cluster = CoexpressionCluster.query.first()

        response = self.client.get('/heatmap/')
        self.assert_template_used('expression_heatmap.html')
        self.assert200(response)

        response = self.client.post('/heatmap/', data=dict(probes=profile.probe, species_id=profile.species_id))
        self.assert_template_used('expression_heatmap.html')
        self.assert200(response)
        self.assertTrue('<td>' + profile.probe + '</td>' in response.data.decode('utf-8'))

        response = self.client.get('/heatmap/cluster/%d' % cluster.id)
        self.assert_template_used('expression_heatmap.html')
        self.assert200(response)

    def test_profile_comparison(self):
        profile = ExpressionProfile.query.first()
        cluster = CoexpressionCluster.query.first()

        response = self.client.get('/profile_comparison/')
        self.assert_template_used('expression_profile_comparison.html')
        self.assert200(response)

        response = self.client.post('/profile_comparison/', data=dict(probes=profile.probe, species_id=profile.species_id, normalize='y'))
        self.assert_template_used('expression_profile_comparison.html')
        self.assert200(response)

        response = self.client.post('/profile_comparison/', data=dict(probes=profile.probe, species_id=profile.species_id, normalize='n'))
        self.assert_template_used('expression_profile_comparison.html')
        self.assert200(response)

        response = self.client.get('/profile_comparison/cluster/%d/%d' % (cluster.id, 0))
        self.assert_template_used('expression_profile_comparison.html')
        self.assert200(response)

        response = self.client.get('/profile_comparison/cluster/%d/%d' % (cluster.id, 1))
        self.assert_template_used('expression_profile_comparison.html')
        self.assert200(response)

    def test_expression_network(self):
        species = Species.query.first()
        expression_network = ExpressionNetwork.query.first()

        response = self.client.get('/network/')
        self.assert_template_used('expression_network.html')
        self.assert200(response)
        self.assertTrue(species.name in response.data.decode('utf-8'))

        response = self.client.get('/network/species/%d' % species.id)
        self.assert_template_used('expression_network.html')
        self.assert200(response)
        self.assertTrue(species.name in response.data.decode('utf-8'))

        response = self.client.get('/network/graph/%d' % expression_network.id)
        self.assert_template_used('expression_graph.html')
        self.assert200(response)

        response = self.client.get('/network/json/%d' % expression_network.id)
        self.assert200(response)
        data = json.loads(response.data.decode('utf-8'))
        self.assertCytoscapeJson(data)

    def test_coexpression_cluster(self):
        species = Species.query.first()
        cluster = CoexpressionCluster.query.first()
        sequence = cluster.sequences.first()
        gf_method = GeneFamilyMethod.query.first()

        response = self.client.get('/cluster/')
        self.assert_template_used('expression_cluster.html')
        self.assert200(response)
        self.assertTrue(species.name in response.data.decode('utf-8'))

        response = self.client.get('/cluster/view/%d' % cluster.id)
        self.assert_template_used('expression_cluster.html')
        self.assert200(response)

        response = self.client.get('/cluster/sequences/%d/%d' % (cluster.id, 1))
        self.assert200(response)
        self.assert_template_used('pagination/cluster_probes.html')
        self.assertTrue(sequence.name in response.data.decode('utf-8'))

        response = self.client.get('/cluster/download/%d' % cluster.id)
        self.assert200(response)
        self.assertTrue(sequence.name in response.data.decode('utf-8'))

        response = self.client.get('/cluster/graph/%d/%d' % (cluster.id, gf_method.id))
        self.assert200(response)
        self.assert_template_used('expression_graph.html')

        response = self.client.get('/cluster/json/%d/%d' % (cluster.id, gf_method.id))
        self.assert200(response)
        data = json.loads(response.data.decode('utf-8'))

        self.assertCytoscapeJson(data)

    def test_graph_comparison(self):
        cluster = CoexpressionCluster.query.first()
        gf_method = GeneFamilyMethod.query.first()

        response = self.client.get('/graph_comparison/cluster/%d/%d/%d' % (cluster.id, cluster.id, gf_method.id))
        self.assert200(response)
        self.assert_template_used('expression_graph.html')

        response = self.client.get('/graph_comparison/cluster/json/%d/%d/%d' % (cluster.id, cluster.id, gf_method.id))
        self.assert200(response)
        data = json.loads(response.data.decode('utf-8'))

        self.assertCytoscapeJson(data)

