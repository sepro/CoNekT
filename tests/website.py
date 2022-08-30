#!/usr/bin/env python3
import json
import unittest

from flask_testing import TestCase

from conekt import create_app, db
from conekt.controllers.help import __TOPICS as topics
from .config import LOGIN_ENABLED, BLAST_ENABLED


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
        app = create_app("tests.config")
        return app

    def setUp(self):
        """
        Creates a database and fills it with sufficient dummy data to run the tests.
        """
        from conekt.models.users import User
        from conekt.models.expression.profiles import ExpressionProfile
        from conekt.models.sequences import Sequence
        from conekt.models.species import Species
        from conekt.models.interpro import Interpro
        from conekt.models.go import GO
        from conekt.models.gene_families import GeneFamily, GeneFamilyMethod
        from conekt.models.expression.coexpression_clusters import (
            CoexpressionCluster,
            CoexpressionClusteringMethod,
        )
        from conekt.models.expression.networks import (
            ExpressionNetwork,
            ExpressionNetworkMethod,
        )
        from conekt.models.relationships.sequence_sequence_ecc import (
            SequenceSequenceECCAssociation,
        )
        from conekt.models.relationships.sequence_cluster import (
            SequenceCoexpressionClusterAssociation,
        )
        from conekt.models.expression.specificity import ExpressionSpecificityMethod
        from conekt.models.clades import Clade

        db.create_all()

        test_user = User("admin", "admin", "", is_admin=True)

        test_species = Species("tst", "Unittest species")
        test_interpro = Interpro("IPR_TEST", "Test label")
        test_go = GO(
            "GO:TEST", "test_process", "biological_process", "Test label", 0, None, None
        )
        test_go2 = GO("GO:TEST2", "test2", "biological_process", "Test", 0, None, None)

        test_gf_method = GeneFamilyMethod("test_gf_method")
        test_gf = GeneFamily("test_gf")

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

        test_sequence = Sequence(
            test_species.id, "TEST_SEQ_01", "ATG", description="test sequence"
        )
        test_sequence.families.append(test_gf)
        test_sequence.interpro_domains.append(test_interpro)
        test_sequence.go_labels.append(test_go)

        test_sequence2 = Sequence(
            test_species.id, "TEST_SEQ_02", "ATG", description="test sequence"
        )
        test_sequence3 = Sequence(
            test_species.id, "TEST_SEQ_03", "ATG", description="test sequence"
        )
        test_sequence3.type = "TE"
        db.session.add(test_sequence)
        db.session.add(test_sequence2)
        db.session.add(test_sequence3)
        db.session.commit()

        test_profile = ExpressionProfile(
            "test_probe",
            test_sequence.id,
            '{"data": {"seedling - hypocotyl 17d": [29.0, 44.0, 35.0], "stage 15 flower - pedicel +21d": [39.0, 18.0, 28.0], "senescing leaf 35d": [104.0, 95.0, 121.0], "stage 12 flower - stamen +21d": [56.0, 41.0, 40.0], "seed - triangle stage 56d": [18.0, 21.0, 37.0], "pollen - uninuclear stage": [17.0, 17.0], "seed - globular stage 56d": [17.0, 28.0, 25.0], "root 21d": [49000.0, 46000.0, 49000.0], "stage 12 flower - carpel +21d": [29.0, 34.0, 38.0], "quiescent center and endodermis, beyond the mature hair zone": [5.0, 5.0, 17.0], "stage 12 flower +21d": [26.0, 39.0, 41.0], "mature seed 56d": [14.0, 12.0, 11.0], "shoot 21d": [94.0, 63.0, 75.0], "stage 10 flower +21d": [83.0, 112.0, 99.0], "stage 12 flower - petal +21d": [68.0, 57.0, 47.0], "seed - heart stage 56d": [44.0, 39.0, 17.0], "stage 1 flower 21d": [126.0, 120.0, 116.0], "stem 2nd internode +21d": [41.0, 42.0, 41.0], "pollen stage 10 - pollen sac  42d": [22.0, 46.0, 31.0], "endodermis, cortex and quiescent center": [13.0, 20.0, 13.0], "rosette leaf 10d": [40.0, 27.0, 44.0], "root 17d": [44.0, 53.0, 51.0], "stage 12 flower - sepal +21d": [56.0, 39.0, 53.0], "stage 9 flower +21d": [113.0, 107.0, 143.0], "~0.15 mm from the root tip": [58.0, 35.0, 17.0, 15.0], "stage 15 flower - carpel +21d": [33.0, 22.0, 24.0], "~0.30 mm from the root tip": [13.0, 13.0, 24.0, 66.0], "rosette leaf - distal half 17d": [18.0, 25.0, 20.0], "petiole 17d": [28.0, 19.0, 20.0], "pollen - bicellular stage": [26.0, 16.0], "atrichoblasts from the quiescent center up": [7.0, 20.0, 8.0], "~0.45 to 2 mm from the root tip": [0.0, 23.0, 20.0, 3.0], "complete rosette 22d": [19.0, 29.0, 24.0], "pollen - tricellular stage": [22.0, 32.0], "stem 1st internode +21d": [72.0, 78.0, 63.0], "stage 15 flower +21d": [32.0, 38.0, 39.0], "pollen - mature": [31.0, 46.0, 22.0], "cauline leaf +21d": [58.0, 41.0, 51.0], "seedling - shoot apex 7d": [27.0, 23.0, 43.0], "complete rosette 23d": [21.0, 20.0, 20.0], "seedling - rosette leaf 7d": [42.0, 40.0, 33.0], "complete rosette 21d": [21.0, 26.0, 22.0], "rosette leaf 17d": [62.0, 57.0, 29.0], "seed - torpedo stage 56d": [24.0, 32.0, 23.0], "rosette leaf - proximal half 17d": [26.0, 17.0, 21.0], "seedling - cotyledon 7d": [50.0, 31.0, 25.0], "stage 15 flower - stamen +21d": [30.0, 18.0, 28.0], "root stele to elongation zone": [20.0, 9.0, 11.0], "stage 15 flower - sepal +21d": [49.0, 28.0, 22.0], "stage 15 flower - petal +21d": [30.0, 19.0, 45.0], "seed - curled cotyledon stage 56d": [16.0, 15.0, 15.0], "lateral root cap and epidermis": [12.0, 6.0, 5.0]}, "order": ["seedling - cotyledon 7d", "seedling - hypocotyl 17d", "seedling - rosette leaf 7d", "seedling - shoot apex 7d", "root 17d", "root 21d", "~0.15 mm from the root tip", "~0.30 mm from the root tip", "~0.45 to 2 mm from the root tip", "atrichoblasts from the quiescent center up", "endodermis, cortex and quiescent center", "lateral root cap and epidermis", "quiescent center and endodermis, beyond the mature hair zone", "root stele to elongation zone", "rosette leaf 10d", "rosette leaf 17d", "rosette leaf - distal half 17d", "rosette leaf - proximal half 17d", "complete rosette 21d", "complete rosette 22d", "complete rosette 23d", "senescing leaf 35d", "cauline leaf +21d", "petiole 17d", "shoot 21d", "stem 1st internode +21d", "stem 2nd internode +21d", "stage 1 flower 21d", "stage 9 flower +21d", "stage 10 flower +21d", "stage 12 flower - carpel +21d", "stage 12 flower - petal +21d", "stage 12 flower - sepal +21d", "stage 12 flower - stamen +21d", "stage 12 flower +21d", "stage 15 flower - carpel +21d", "stage 15 flower - pedicel +21d", "stage 15 flower - petal +21d", "stage 15 flower - sepal +21d", "stage 15 flower - stamen +21d", "stage 15 flower +21d", "seed - curled cotyledon stage 56d", "seed - globular stage 56d", "seed - heart stage 56d", "seed - torpedo stage 56d", "seed - triangle stage 56d", "mature seed 56d", "pollen stage 10 - pollen sac  42d", "pollen - uninuclear stage", "pollen - bicellular stage", "pollen - tricellular stage", "pollen - mature"]}',
        )
        test_profile.species_id = test_species.id
        test_profile2 = ExpressionProfile(
            "test_probe2",
            test_sequence2.id,
            '{"data": {"seedling - hypocotyl 17d": [29.0, 44.0, 35.0], "stage 15 flower - pedicel +21d": [39.0, 18.0, 28.0], "senescing leaf 35d": [104.0, 95.0, 121.0], "stage 12 flower - stamen +21d": [56.0, 41.0, 40.0], "seed - triangle stage 56d": [18.0, 21.0, 37.0], "pollen - uninuclear stage": [17.0, 17.0], "seed - globular stage 56d": [17.0, 28.0, 25.0], "root 21d": [49.0, 46.0, 49.0], "stage 12 flower - carpel +21d": [29.0, 34.0, 38.0], "quiescent center and endodermis, beyond the mature hair zone": [5.0, 5.0, 17.0], "stage 12 flower +21d": [26.0, 39.0, 41.0], "mature seed 56d": [14.0, 12.0, 11.0], "shoot 21d": [94.0, 63.0, 75.0], "stage 10 flower +21d": [83.0, 112.0, 99.0], "stage 12 flower - petal +21d": [68.0, 57.0, 47.0], "seed - heart stage 56d": [44.0, 39.0, 17.0], "stage 1 flower 21d": [126.0, 120.0, 116.0], "stem 2nd internode +21d": [41.0, 42.0, 41.0], "pollen stage 10 - pollen sac  42d": [22.0, 46.0, 31.0], "endodermis, cortex and quiescent center": [13.0, 20.0, 13.0], "rosette leaf 10d": [40.0, 27.0, 44.0], "root 17d": [44.0, 53.0, 51.0], "stage 12 flower - sepal +21d": [56.0, 39.0, 53.0], "stage 9 flower +21d": [113.0, 107.0, 143.0], "~0.15 mm from the root tip": [58.0, 35.0, 17.0, 15.0], "stage 15 flower - carpel +21d": [33.0, 22.0, 24.0], "~0.30 mm from the root tip": [13.0, 13.0, 24.0, 66.0], "rosette leaf - distal half 17d": [18.0, 25.0, 20.0], "petiole 17d": [28.0, 19.0, 20.0], "pollen - bicellular stage": [26.0, 16.0], "atrichoblasts from the quiescent center up": [7.0, 20.0, 8.0], "~0.45 to 2 mm from the root tip": [0.0, 23.0, 20.0, 3.0], "complete rosette 22d": [19.0, 29.0, 24.0], "pollen - tricellular stage": [22.0, 32.0], "stem 1st internode +21d": [72.0, 78.0, 63.0], "stage 15 flower +21d": [32.0, 38.0, 39.0], "pollen - mature": [31.0, 46.0, 22.0], "cauline leaf +21d": [58.0, 41.0, 51.0], "seedling - shoot apex 7d": [27.0, 23.0, 43.0], "complete rosette 23d": [21.0, 20.0, 20.0], "seedling - rosette leaf 7d": [42.0, 40.0, 33.0], "complete rosette 21d": [21.0, 26.0, 22.0], "rosette leaf 17d": [62.0, 57.0, 29.0], "seed - torpedo stage 56d": [24.0, 32.0, 23.0], "rosette leaf - proximal half 17d": [26.0, 17.0, 21.0], "seedling - cotyledon 7d": [50.0, 31.0, 25.0], "stage 15 flower - stamen +21d": [30.0, 18.0, 28.0], "root stele to elongation zone": [20.0, 9.0, 11.0], "stage 15 flower - sepal +21d": [49.0, 28.0, 22.0], "stage 15 flower - petal +21d": [30.0, 19.0, 45.0], "seed - curled cotyledon stage 56d": [16.0, 15.0, 15.0], "lateral root cap and epidermis": [12.0, 6.0, 5.0]}, "order": ["seedling - cotyledon 7d", "seedling - hypocotyl 17d", "seedling - rosette leaf 7d", "seedling - shoot apex 7d", "root 17d", "root 21d", "~0.15 mm from the root tip", "~0.30 mm from the root tip", "~0.45 to 2 mm from the root tip", "atrichoblasts from the quiescent center up", "endodermis, cortex and quiescent center", "lateral root cap and epidermis", "quiescent center and endodermis, beyond the mature hair zone", "root stele to elongation zone", "rosette leaf 10d", "rosette leaf 17d", "rosette leaf - distal half 17d", "rosette leaf - proximal half 17d", "complete rosette 21d", "complete rosette 22d", "complete rosette 23d", "senescing leaf 35d", "cauline leaf +21d", "petiole 17d", "shoot 21d", "stem 1st internode +21d", "stem 2nd internode +21d", "stage 1 flower 21d", "stage 9 flower +21d", "stage 10 flower +21d", "stage 12 flower - carpel +21d", "stage 12 flower - petal +21d", "stage 12 flower - sepal +21d", "stage 12 flower - stamen +21d", "stage 12 flower +21d", "stage 15 flower - carpel +21d", "stage 15 flower - pedicel +21d", "stage 15 flower - petal +21d", "stage 15 flower - sepal +21d", "stage 15 flower - stamen +21d", "stage 15 flower +21d", "seed - curled cotyledon stage 56d", "seed - globular stage 56d", "seed - heart stage 56d", "seed - torpedo stage 56d", "seed - triangle stage 56d", "mature seed 56d", "pollen stage 10 - pollen sac  42d", "pollen - uninuclear stage", "pollen - bicellular stage", "pollen - tricellular stage", "pollen - mature"]}',
        )
        test_profile2.species_id = test_species.id
        db.session.add(test_profile)
        db.session.add(test_profile2)
        db.session.commit()

        test_expression_network_method = ExpressionNetworkMethod(
            test_species.id, "Test network method"
        )
        test_expression_network_method.pcc_cutoff = 0.0
        test_expression_network_method.hrr_cutoff = 100
        test_expression_network_method.enable_second_level = 0
        db.session.add(test_expression_network_method)
        db.session.commit()

        test_expression_network = ExpressionNetwork(
            test_profile.probe,
            test_sequence.id,
            '[{"gene_name": "TEST_SEQ_02", "gene_id": '
            + str(test_sequence2.id)
            + ', "probe_name": "test_probe2", "link_score": 0, "hrr":0}]',
            test_expression_network_method.id,
        )

        test_expression_network2 = ExpressionNetwork(
            test_profile2.probe,
            test_sequence2.id,
            '[{"gene_name": "TEST_SEQ_01", "gene_id": '
            + str(test_sequence.id)
            + ', "probe_name": "test_probe2", "link_score": 0, "hrr":0}]',
            test_expression_network_method.id,
        )

        db.session.add(test_expression_network)
        db.session.add(test_expression_network2)
        db.session.commit()

        test_expression_network_method.update_count()

        test_cluster_method = CoexpressionClusteringMethod()
        test_cluster_method.network_method_id = test_expression_network_method.id
        test_cluster_method.method = "test clustering method"

        db.session.add(test_cluster_method)
        db.session.commit()

        test_cluster = CoexpressionCluster()
        test_cluster.method_id = test_cluster_method.id
        test_cluster.name = "TEST_COEXP_CLUSTER"

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

        Clade.add_clade("test", ["tst"], "(test:0.01);")
        clade = Clade.query.first()
        clade.families.append(GeneFamily.query.first())
        clade.interpro.append(Interpro.query.first())
        db.session.commit()

        new_ecc = SequenceSequenceECCAssociation()
        new_ecc.query_id = test_sequence.id
        new_ecc.target_id = test_sequence2.id
        new_ecc.gene_family_method_id = test_gf_method.id
        new_ecc.query_network_method_id = test_expression_network_method.id
        new_ecc.target_network_method_id = test_expression_network_method.id
        new_ecc.ecc = 0.5
        new_ecc.p_value = 0.05
        new_ecc.corrected_p_value = 0.05

        db.session.add(new_ecc)
        db.session.commit()

        ExpressionSpecificityMethod.calculate_specificities(
            test_species.id, "Specificity description"
        )

        test_species.update_counts()
        clade.update_clades()
        clade.update_clades_interpro()

    def tearDown(self):
        """
        Removes test database again, so the next test can start with a clean slate
        """
        db.session.remove()
        db.drop_all()

    def assertCytoscapeJson(self, data, ecc_graph=False):
        self.assertTrue("nodes" in data.keys())
        self.assertTrue("edges" in data.keys())

        for node in data["nodes"]:
            self.assertTrue("color" in node["data"].keys())
            self.assertTrue("id" in node["data"].keys())

            compound = (
                node["data"]["compound"] if "compound" in node["data"].keys() else False
            )

            if not compound:
                required_keys = [
                    "family_color",
                    "lc_label",
                    "lc_color",
                    "lc_shape",
                    "family_name",
                    "shape",
                    "description",
                    "name",
                    "gene_name",
                    "tokens",
                    "family_clade_count",
                    "gene_id",
                    "family_id",
                    "family_url",
                    "family_clade",
                    "family_shape",
                ]

                self.assertTrue("data" in node.keys())
                self.assertTrue(all([k in node["data"].keys() for k in required_keys]))

                if not ecc_graph:
                    self.assertTrue("depth" in node["data"].keys())
                    self.assertTrue("profile_link" in node["data"].keys())
                else:
                    self.assertTrue("species_name" in node["data"].keys())
                    self.assertTrue("species_id" in node["data"].keys())
                    self.assertTrue("species_color" in node["data"].keys())

        for edge in data["edges"]:
            self.assertTrue("data" in edge.keys())
            self.assertTrue("source" in edge["data"].keys())
            self.assertTrue("target" in edge["data"].keys())
            self.assertTrue("color" in edge["data"].keys())

            homology = (
                edge["data"]["homology"] if "homology" in edge["data"].keys() else False
            )

            if not homology:
                self.assertTrue("edge_type" in edge["data"].keys())
                if not ecc_graph:
                    self.assertTrue("link_score" in edge["data"].keys())
                    self.assertTrue("profile_comparison" in edge["data"].keys())
                    self.assertTrue("depth" in edge["data"].keys())
                else:
                    self.assertTrue("ecc_score" in edge["data"].keys())

    def test_main(self):
        response = self.client.get("/")
        self.assert_template_used("static_pages/main.html")
        self.assert200(response)

        response = self.client.get("/about")
        self.assert_template_used("static_pages/about.html")
        self.assert200(response)

        response = self.client.get("/contact")
        self.assert_template_used("static_pages/contact.html")
        self.assert200(response)

        response = self.client.get("/disclaimer")
        self.assert_template_used("static_pages/disclaimer.html")
        self.assert200(response)

        response = self.client.get("/features")
        self.assert_template_used("static_pages/features.html")
        self.assert200(response)

        response = self.client.get("/this_should_not_exist")
        self.assert_template_used("error/404.html")
        self.assert404(response)

    def test_sequence(self):
        """
        Test for routes associated with a Sequence
        """
        from conekt.models.sequences import Sequence

        sequence = Sequence.query.first()

        response = self.client.get("/sequence/")
        self.assertRedirects(response, "/")

        response = self.client.get("/sequence/view/%d" % sequence.id)
        self.assert_template_used("sequence.html")
        self.assert200(response)

        response = self.client.get("/sequence/tooltip/%d" % sequence.id)
        self.assert_template_used("tooltips/sequence.html")
        self.assert200(response)

        response = self.client.get("/sequence/modal/coding/%d" % sequence.id)
        self.assert_template_used("modals/sequence.html")
        self.assert200(response)

        response = self.client.get("/sequence/modal/protein/%d" % sequence.id)
        self.assert_template_used("modals/sequence.html")
        self.assert200(response)

        response = self.client.get("/sequence/fasta/coding/%d" % sequence.id)
        self.assert200(response)
        data = response.data.decode("utf-8").strip()
        self.assertEqual(len(data.split("\n")), 2)
        self.assertEqual(data[0], ">")
        self.assertTrue(">" + sequence.name + "\n" in data)

        response = self.client.get("/sequence/fasta/protein/%d" % sequence.id)
        self.assert200(response)
        data = response.data.decode("utf-8").strip()
        self.assertEqual(len(data.split("\n")), 2)
        self.assertEqual(data[0], ">")
        self.assertTrue(">" + sequence.name + "\n" in data)

        response = self.client.get(
            "/sequence/find/" + sequence.name, follow_redirects=True
        )
        self.assert_template_used("sequence.html")
        self.assert200(response)

        response = self.client.get("/sequence/view/a")
        self.assert404(response)

    def test_species(self):
        """
        Test for routes associated with a Species
        """
        from conekt.models.species import Species

        # Should have a main page
        response = self.client.get("/species/")
        self.assert_template_used("species.html")
        self.assert200(response)

        species = Species.query.first()
        sequence = species.sequences.first()

        # Should respresent itself as a string
        self.assertEqual(str(species), str(species.id) + ". " + species.name)

        # Should have a detailed page for each species
        response = self.client.get("/species/view/%d" % species.id)
        self.assert_template_used("species.html")
        self.assert200(response)

        # Should have a paginated page with the sequences
        response = self.client.get("/species/sequences/%d/1" % species.id)
        self.assert_template_used("pagination/sequences.html")
        self.assert200(response)

        # Should have allow downloading coding sequences as a fasta file
        response = self.client.get("/species/download/coding/%d" % species.id)
        self.assert200(response)
        data = response.data.decode("utf-8").strip()
        self.assertTrue(len(data.split("\n")) > 0)
        self.assertEqual(data[0], ">")
        self.assertTrue(">" + sequence.name + "\n" in data)

        # Should have allow downloading protein sequences as a fasta file
        response = self.client.get("/species/download/protein/%d" % species.id)
        self.assert200(response)
        data = response.data.decode("utf-8").strip()
        self.assertTrue(len(data.split("\n")) > 0)
        self.assertEqual(data[0], ">")
        self.assertTrue(">" + sequence.name + "\n" in data)

        # Should have allow streaming coding sequences as a fasta file
        response = self.client.get("/species/stream/coding/%d" % species.id)
        self.assert200(response)
        data = response.data.decode("utf-8").strip()
        self.assertTrue(len(data.split("\n")) > 0)
        self.assertEqual(data[0], ">")
        self.assertTrue(">" + sequence.name + "\n" in data)

        # Should have allow streaming protein sequences as a fasta file
        response = self.client.get("/species/stream/protein/%d" % species.id)
        self.assert200(response)
        data = response.data.decode("utf-8").strip()
        self.assertTrue(len(data.split("\n")) > 0)
        self.assertEqual(data[0], ">")
        self.assertTrue(">" + sequence.name + "\n" in data)

    def test_interpro(self):
        """
        Test for routes associated with an InterPro domain
        """
        from conekt.models.interpro import Interpro

        # Should redirect to main page as there is no overview
        response = self.client.get("/interpro/")
        self.assertRedirects(response, "/")

        interpro = Interpro.query.first()

        # Should show page for each domain
        response = self.client.get("/interpro/view/%d" % interpro.id)
        self.assert_template_used("interpro.html")
        self.assert200(response)

        # Should find domains based on their label
        response = self.client.get(
            "/interpro/find/" + interpro.label, follow_redirects=True
        )
        self.assert_template_used("interpro.html")
        self.assert200(response)

        # Should show sequences that have the domain
        response = self.client.get("/interpro/sequences/%d/1" % interpro.id)
        self.assert_template_used("pagination/sequences.html")
        self.assert200(response)

        # Should allow downloading sequences that have the domain as csv
        response = self.client.get("/interpro/sequences/table/%d" % interpro.id)
        self.assert_template_used("tables/sequences.csv")
        self.assert200(response)

        # Should return phylogenetic profile compatible with charts.js
        response = self.client.get("/interpro/json/species/%d" % interpro.id)
        self.assert200(response)

        data = json.loads(response.data.decode("utf-8"))

        self.assertTrue("data" in data.keys())
        self.assertTrue("type" in data.keys())

        self.assertTrue("labels" in data["data"].keys())
        self.assertTrue("datasets" in data["data"].keys())

    def test_go(self):
        """
        Test for routes associated with a GO label
        """
        from conekt.models.go import GO

        response = self.client.get("/go/")
        self.assertRedirects(response, "/")

        go = GO.query.first()

        response = self.client.get("/go/view/%d" % go.id)
        self.assert_template_used("go.html")
        self.assert200(response)

        response = self.client.get("/go/find/" + go.label)
        self.assertRedirects(response, "/go/view/%d" % go.id)

        response = self.client.get("/go/sequences/%d/1" % go.id)
        self.assert_template_used("pagination/sequences.html")
        self.assert200(response)

        response = self.client.get("/go/sequences/table/%d" % go.id)
        self.assert_template_used("tables/sequences.csv")
        self.assert200(response)

        response = self.client.get("/go/json/species/%d" % go.id)
        self.assert200(response)

        data = json.loads(response.data.decode("utf-8"))

        self.assertTrue("data" in data.keys())
        self.assertTrue("type" in data.keys())

        self.assertTrue("labels" in data["data"].keys())
        self.assertTrue("datasets" in data["data"].keys())

        response = self.client.get("/go/json/genes/" + go.label)
        self.assert200(response)

        data = json.loads(response.data.decode("utf-8"))
        self.assertTrue(1 in data)

        response = self.client.get("/go/json/genes/" + "no_label")
        self.assert200(response)

        data = json.loads(response.data.decode("utf-8"))
        self.assertTrue(data == [])

    def test_family(self):
        """
        Test for routes associated with a GeneFamily
        """
        from conekt.models.gene_families import GeneFamily

        response = self.client.get("/family/")
        self.assertRedirects(response, "/")

        family = GeneFamily.query.first()

        response = self.client.get("/family/view/%d" % family.id)
        self.assert_template_used("family.html")
        self.assert200(response)

        response = self.client.get("/family/find/" + family.name, follow_redirects=True)
        self.assert_template_used("family.html")
        self.assert200(response)

        response = self.client.get("/family/sequences/%d/1" % family.id)
        self.assert_template_used("pagination/sequences.html")
        self.assert200(response)

        response = self.client.get("/family/sequences/table/%d" % family.id)
        self.assert_template_used("tables/sequences.csv")
        self.assert200(response)

        response = self.client.get("/family/json/species/%d" % family.id)
        self.assert200(response)

        data = json.loads(response.data.decode("utf-8"))

        self.assertTrue("data" in data.keys())
        self.assertTrue("type" in data.keys())

        self.assertTrue("labels" in data["data"].keys())
        self.assertTrue("datasets" in data["data"].keys())

    def test_profile(self):
        """
        Test for routes associated with an ExpressionProfile
        """
        from conekt.models.expression.profiles import ExpressionProfile

        response = self.client.get("/profile/")
        self.assertRedirects(response, "/")

        profile = ExpressionProfile.query.first()

        response = self.client.get("/profile/view/%d" % profile.id)
        self.assert_template_used("expression_profile.html")
        self.assert200(response)

        response = self.client.get("/profile/modal/%d" % profile.id)
        self.assert_template_used("modals/expression_profile.html")
        self.assert200(response)

        response = self.client.get(
            "/profile/find/" + profile.probe, follow_redirects=True
        )
        self.assert200(response)
        self.assert_template_used("expression_profile.html")

        response = self.client.get("/profile/find/%s/%d" % (profile.probe, 2))
        self.assert404(response)

        response = self.client.get("/profile/compare/%d/%d" % (profile.id, profile.id))
        self.assert_template_used("compare_profiles.html")
        self.assert200(response)

        response = self.client.get(
            "/profile/compare_probes/%s/%s/%d" % (profile.probe, profile.probe, 1)
        )
        self.assert_template_used("compare_profiles.html")
        self.assert200(response)

        response = self.client.get(
            "/profile/compare_probes/%s/%s/%d" % (profile.probe, profile.probe, 2)
        )
        self.assert404(response)

        response = self.client.get("/profile/json/plot/%d" % profile.id)
        self.assert200(response)

        data = json.loads(response.data.decode("utf-8"))
        self.assertTrue("type" in data.keys())
        self.assertTrue("data" in data.keys())
        self.assertTrue("labels" in data["data"].keys())
        self.assertTrue("datasets" in data["data"].keys())
        for i in range(len(data["data"]["datasets"])):
            self.assertTrue("data" in data["data"]["datasets"][i].keys())

        response = self.client.get(
            "/profile/json/compare_plot/%d/%d" % (profile.id, profile.id)
        )
        self.assert200(response)

        data = json.loads(response.data.decode("utf-8"))
        self.assertTrue("type" in data.keys())
        self.assertTrue("data" in data.keys())
        self.assertTrue("labels" in data["data"].keys())
        self.assertTrue("datasets" in data["data"].keys())
        for i in range(len(data["data"]["datasets"])):
            self.assertTrue("data" in data["data"]["datasets"][i].keys())

    def test_help(self):
        """
        Test for help pages (which are static)
        """
        for k, v in topics.items():
            response = self.client.get("/help/%s" % k)
            self.assert_template_used(v)
            self.assert200(response)

        response = self.client.get("/help/%s" % "term_does_not_exist")
        self.assert404(response)

    def test_search(self):
        """
        Test different components of the search function
        """
        from conekt.models.sequences import Sequence
        from conekt.models.interpro import Interpro
        from conekt.models.go import GO
        from conekt.models.gene_families import GeneFamily
        from conekt.models.expression.profiles import ExpressionProfile

        sequence = Sequence.query.first()
        interpro = Interpro.query.first()
        go = GO.query.first()
        family = GeneFamily.query.first()
        expression_profile = ExpressionProfile.query.first()

        response = self.client.get("/search/keyword/%s" % sequence.name)
        self.assertRedirects(response, "/sequence/view/%d" % sequence.id)

        response = self.client.get("/search/keyword/%s" % interpro.label)
        self.assertRedirects(response, "/interpro/view/%d" % interpro.id)

        response = self.client.get("/search/keyword/%s" % go.label)
        self.assertRedirects(response, "/go/view/%d" % go.id)

        response = self.client.get("/search/keyword/%s" % family.name)
        self.assertRedirects(response, "/family/view/%d" % family.id)

        response = self.client.get("/search/keyword/%s" % expression_profile.probe)
        self.assertRedirects(response, "/profile/view/%d" % expression_profile.id)

        response = self.client.get("/search/keyword/%s" % "t")
        self.assert_template_used("search_results.html")
        self.assert200(response)

        response = self.client.get("/search/")
        self.assertRedirects(response, "/")

        response = self.client.post("/search/", data=dict(terms="TEST_SEQ_01"))
        self.assertRedirects(response, "/sequence/view/%d" % sequence.id)

        response = self.client.post("/search/", data=dict(terms=family.name))
        self.assertRedirects(response, "/family/view/%d" % family.id)

        response = self.client.post("/search/", data=dict(terms=go.label))
        self.assertRedirects(response, "/go/view/%d" % go.id)

        response = self.client.post("/search/", data=dict(terms=interpro.label))
        self.assertRedirects(response, "/interpro/view/%d" % interpro.id)

        response = self.client.post(
            "/search/", data=dict(terms=expression_profile.probe)
        )
        self.assertRedirects(response, "/profile/view/%d" % expression_profile.id)

        response = self.client.post(
            "/search/",
            data=dict(
                terms=" ".join(
                    [
                        family.name,
                        sequence.name,
                        interpro.label,
                        expression_profile.probe,
                    ]
                )
            ),
        )
        self.assert_template_used("search_results.html")
        self.assert200(response)

        response = self.client.post("/search/", data=dict(terms="Test label"))
        self.assert_template_used("search_results.html")
        self.assert200(response)

        response = self.client.get("/search/json/genes/%s" % go.label)
        self.assert200(response)
        data = json.loads(response.data.decode("utf-8"))
        self.assertTrue(sequence.id in data)

        # TODO: search_enriched_clusters() is currently untested !

        response = self.client.get("/search/typeahead/go/prefetch")
        self.assert200(response)
        data = json.loads(response.data.decode("utf-8"))
        self.assertTrue(len(data) == 1)
        for d in data:
            self.assertTrue("value" in d.keys())
            self.assertTrue("tokens" in d.keys())

        response = self.client.get("/search/typeahead/go/test.json")
        self.assert200(response)
        data = json.loads(response.data.decode("utf-8"))
        self.assertTrue(len(data) == 2)
        for d in data:
            self.assertTrue("value" in d.keys())
            self.assertTrue("tokens" in d.keys())

    def test_advanced_search(self):
        """
        Test different components of the search function
        """
        response = self.client.get("/search/advanced")
        self.assert200(response)
        self.assert_template_used("search_advanced.html")

    @unittest.skipIf(
        not LOGIN_ENABLED, "Skipping test_auth because LOGIN is not enabled"
    )
    def test_auth(self):
        """
        Test if a user can log in
        """
        response = self.client.get("/auth/login")
        self.assert_template_used("login.html")
        self.assert200(response)

        response = self.client.post(
            "/auth/login",
            data=dict(username="admin", password="admin", keep_logged="y"),
            follow_redirects=True,
        )
        self.assert200(response)
        self.assertTrue(
            "You have successfully logged in." in response.data.decode("utf-8")
        )

        response = self.client.get("/auth/logout", follow_redirects=True)
        self.assert200(response)
        self.assertTrue(
            "You have successfully logged out." in response.data.decode("utf-8")
        )

        response = self.client.post(
            "/auth/login",
            data=dict(username="admin", password="wrong", keep_logged="y"),
            follow_redirects=True,
        )
        self.assert200(response)
        self.assertTrue(
            "Invalid username or password. Please try again."
            in response.data.decode("utf-8")
        )

    @unittest.skipIf(not BLAST_ENABLED, "Skipping test because BLAST is not enabled")
    def test_blast(self):
        """
        Test basic components of the BLAST search

        TODO: check if BLAST is configured correctly !
        """
        response = self.client.get("/blast/")
        self.assert_template_used("blast.html")
        self.assert200(response)

        response = self.client.get("/blast/results/testtoken")
        self.assert_template_used("blast.html")
        self.assert200(response)

        response = self.client.get("/blast/results/json/testtoken")
        self.assert200(response)
        data = json.loads(response.data.decode("utf-8"))
        self.assertTrue("status" in data)

    def test_heatmap(self):
        from conekt.models.expression.profiles import ExpressionProfile
        from conekt.models.expression.coexpression_clusters import CoexpressionCluster

        profile = ExpressionProfile.query.first()
        cluster = CoexpressionCluster.query.first()

        response = self.client.get("/heatmap/")
        self.assert_template_used("expression_heatmap.html")
        self.assert200(response)

        response = self.client.post(
            "/heatmap/", data=dict(probes=profile.probe, species_id=profile.species_id)
        )
        self.assert_template_used("expression_heatmap.html")
        self.assert200(response)
        self.assertTrue(profile.probe in response.data.decode("utf-8"))

        response = self.client.get("/heatmap/cluster/%d" % cluster.id)
        self.assert_template_used("expression_heatmap.html")
        self.assert200(response)

        response = self.client.get("/heatmap/inchlib/j/%d.json" % cluster.id)
        self.assert200(response)
        data = json.loads(response.data.decode("utf-8"))
        self.assertTrue("data" in data.keys())
        self.assertTrue("nodes" in data["data"])
        self.assertTrue("feature_names" in data["data"])

        response = self.client.get("/heatmap/inchlib/%d" % cluster.id)
        self.assert_template_used("inchlib_heatmap.html")
        self.assert200(response)

    def test_profile_comparison(self):
        from conekt.models.expression.profiles import ExpressionProfile
        from conekt.models.expression.coexpression_clusters import CoexpressionCluster

        profile = ExpressionProfile.query.first()
        cluster = CoexpressionCluster.query.first()

        response = self.client.get("/profile_comparison/")
        self.assert_template_used("expression_profile_comparison.html")
        self.assert200(response)

        response = self.client.post(
            "/profile_comparison/",
            data=dict(
                probes=profile.probe, species_id=profile.species_id, normalize="y"
            ),
        )
        self.assert_template_used("expression_profile_comparison.html")
        self.assert200(response)

        response = self.client.post(
            "/profile_comparison/",
            data=dict(
                probes=profile.probe, species_id=profile.species_id, normalize="n"
            ),
        )
        self.assert_template_used("expression_profile_comparison.html")
        self.assert200(response)

        response = self.client.get(
            "/profile_comparison/cluster/%d/%d" % (cluster.id, 0)
        )
        self.assert_template_used("expression_profile_comparison.html")
        self.assert200(response)

        response = self.client.get(
            "/profile_comparison/cluster/%d/%d" % (cluster.id, 1)
        )
        self.assert_template_used("expression_profile_comparison.html")
        self.assert200(response)

    def test_expression_network(self):
        from conekt.models.species import Species
        from conekt.models.expression.networks import ExpressionNetwork

        species = Species.query.first()
        expression_network = ExpressionNetwork.query.first()

        response = self.client.get("/network/")
        self.assert_template_used("expression_network.html")
        self.assert200(response)
        self.assertTrue(species.name in response.data.decode("utf-8"))

        response = self.client.get("/network/species/%d" % species.id)
        self.assert_template_used("expression_network.html")
        self.assert200(response)
        self.assertTrue(species.name in response.data.decode("utf-8"))

        response = self.client.get("/network/graph/%d" % expression_network.id)
        self.assert_template_used("expression_graph.html")
        self.assert200(response)

        response = self.client.get("/network/json/%d" % expression_network.id)
        self.assert200(response)
        data = json.loads(response.data.decode("utf-8"))
        self.assertCytoscapeJson(data)

    def test_coexpression_cluster(self):
        # from planet.models.species import Species
        from conekt.models.expression.coexpression_clusters import CoexpressionCluster
        from conekt.models.gene_families import GeneFamilyMethod

        # species = Species.query.first()
        cluster = CoexpressionCluster.query.first()
        sequence = cluster.sequences.first()
        gf_method = GeneFamilyMethod.query.first()

        response = self.client.get("/cluster/")
        self.assert_template_used("expression_cluster.html")
        self.assert200(response)
        # self.assertTrue(species.name in response.data.decode('utf-8'))

        response = self.client.get("/cluster/view/%d" % cluster.id)
        self.assert_template_used("expression_cluster.html")
        self.assert200(response)

        response = self.client.get("/cluster/sequences/%d/%d" % (cluster.id, 1))
        self.assert200(response)
        self.assert_template_used("pagination/cluster_probes.html")
        self.assertTrue(sequence.name in response.data.decode("utf-8"))

        response = self.client.get("/cluster/download/%d" % cluster.id)
        self.assert200(response)
        self.assertTrue(sequence.name in response.data.decode("utf-8"))

        response = self.client.get("/cluster/graph/%d/%d" % (cluster.id, gf_method.id))
        self.assert200(response)
        self.assert_template_used("expression_graph.html")

        response = self.client.get("/cluster/json/%d/%d" % (cluster.id, gf_method.id))
        self.assert200(response)
        data = json.loads(response.data.decode("utf-8"))

        self.assertCytoscapeJson(data)

    def test_graph_comparison(self):
        from conekt.models.expression.coexpression_clusters import CoexpressionCluster
        from conekt.models.gene_families import GeneFamilyMethod

        cluster = CoexpressionCluster.query.first()
        gf_method = GeneFamilyMethod.query.first()

        response = self.client.get(
            "/graph_comparison/cluster/%d/%d/%d"
            % (cluster.id, cluster.id, gf_method.id)
        )
        self.assert200(response)
        self.assert_template_used("expression_graph.html")

        response = self.client.get(
            "/graph_comparison/cluster/json/%d/%d/%d"
            % (cluster.id, cluster.id, gf_method.id)
        )
        self.assert200(response)
        data = json.loads(response.data.decode("utf-8"))

        self.assertCytoscapeJson(data)

    def test_clades(self):
        from conekt.models.clades import Clade
        from conekt.models.gene_families import GeneFamily
        from conekt.models.interpro import Interpro

        clade = Clade.query.first()
        family = GeneFamily.query.first()
        interpro = Interpro.query.first()

        response = self.client.get("/clade/")
        self.assertRedirects(response, "/")

        response = self.client.get("/clade/view/%d" % clade.id)
        self.assert200(response)
        self.assert_template_used("clade.html")

        response = self.client.get("/clade/families/%d/1" % clade.id)
        self.assert200(response)
        self.assert_template_used("pagination/families.html")

        response = self.client.get("/clade/families/table/%d" % clade.id)
        self.assert200(response)
        self.assert_template_used("tables/families.csv")
        self.assertTrue(family.name in response.data.decode("utf-8"))

        response = self.client.get("/clade/interpro/%d/1" % clade.id)
        self.assert200(response)
        self.assert_template_used("pagination/interpro.html")

        response = self.client.get("/clade/interpro/table/%d" % clade.id)
        self.assert200(response)
        self.assert_template_used("tables/interpro.csv")
        self.assertTrue(interpro.label in response.data.decode("utf-8"))

    def test_ecc(self):
        from conekt.models.relationships.sequence_sequence_ecc import (
            SequenceSequenceECCAssociation,
        )

        ecc = SequenceSequenceECCAssociation.query.first()

        response = self.client.get("/ecc/")
        self.assertRedirects(response, "/")

        response = self.client.get(
            "/ecc/graph/%d/%d/%d"
            % (ecc.query_id, ecc.query_network_method_id, ecc.gene_family_method.id)
        )
        self.assert200(response)
        self.assert_template_used("expression_graph.html")

        response = self.client.get(
            "/ecc/json/%d/%d/%d"
            % (ecc.query_id, ecc.query_network_method_id, ecc.gene_family_method.id)
        )
        self.assert200(response)
        data = json.loads(response.data.decode("utf-8"))

        self.assertCytoscapeJson(data, ecc_graph=True)

    def test_specificity_search(self):
        from conekt.models.sequences import Sequence

        response = self.client.get("/search/specific/profiles")
        self.assert200(response)
        self.assert_template_used("find_specific_profiles.html")

        # first gene should be in the results
        sequence = Sequence.query.first()

        response = self.client.post(
            "/search/specific/profiles",
            data=dict(species=1, methods=1, conditions="root 21d", cutoff=0.85),
        )
        self.assert200(response)
        self.assert_template_used("find_specific_profiles.html")
        self.assertTrue(sequence.name in response.data.decode("utf-8"))
