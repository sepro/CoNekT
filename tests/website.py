#!/usr/bin/env python3
from planet import create_app, db

from planet.models.sequences import Sequence
from planet.models.species import Species
from planet.models.interpro import Interpro
from planet.models.go import GO
from planet.models.gene_families import GeneFamily, GeneFamilyMethod

from flask.ext.testing import TestCase

import sys


class WebsiteTest(TestCase):

    def create_app(self):
        app = create_app('tests.config')
        return app

    def setUp(self):
        db.create_all()

        # Add dummy data

        test_species = Species('tst', 'Unittest species')
        test_interpro = Interpro('IPR_TEST', 'Test label')
        test_go = GO('GO:TEST', 'test_process', 'biological_process',  'Test label', False, None, None)

        test_gf_method = GeneFamilyMethod('test_gf_method')
        test_gf = GeneFamily('test_gf')

        db.session.add(test_species)
        db.session.add(test_interpro)
        db.session.add(test_go)
        db.session.add(test_gf_method)
        db.session.add(test_gf)
        db.session.commit()

        test_gf.method_id = test_gf_method.id

        db.session.commit()

        test_sequence = Sequence(test_species.id, 'TEST_SEQ_01', 'ATG', description='test sequence')
        test_sequence.families.append(test_gf)
        test_sequence.interpro_domains.append(test_interpro)
        test_sequence.go_labels.append(test_go)

        db.session.add(test_sequence)
        db.session.commit()

    def tearDown(self):

        db.session.remove()
        db.drop_all()

    def test_sequence(self):
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

            response = self.client.get("/sequence/fasta/protein/%d" % sequence.id)
            self.assert200(response)

            data = response.data.decode("utf-8").strip()
            self.assertEqual(len(data.split('\n')), 2)
            self.assertEqual(data[0], '>')

            response = self.client.get("/sequence/find/" + sequence.name)
            self.assert_template_used('sequence.html')
            self.assert200(response)

            response = self.client.get("/sequence/view/a")
            self.assert404(response)
        else:
            print('  * test_sequence: No sequence found, skipping test...', file=sys.stderr)

    def test_species(self):
        response = self.client.get("/species/")
        self.assert_template_used('species.html')
        self.assert200(response)

        species = Species.query.first()
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

            response = self.client.get("/species/download/protein/%d" % species.id)
            self.assert200(response)

            data = response.data.decode("utf-8").strip()
            self.assertTrue(len(data.split('\n')) > 0)
            self.assertEqual(data[0], '>')

            response = self.client.get("/species/stream/coding/%d" % species.id)
            self.assert200(response)

            data = response.data.decode("utf-8").strip()
            self.assertTrue(len(data.split('\n')) > 0)
            self.assertEqual(data[0], '>')

            response = self.client.get("/species/stream/protein/%d" % species.id)
            self.assert200(response)

            data = response.data.decode("utf-8").strip()
            self.assertTrue(len(data.split('\n')) > 0)
            self.assertEqual(data[0], '>')

        else:
            print('  * test_species: No species found, skipping test...', file=sys.stderr)

    def test_interpro(self):
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
        else:
            print('  * test_interpro: No interpro domain found, skipping test...', file=sys.stderr)

    def test_go(self):
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

            response = self.client.get("/go/json/genes/" + go.label)
            self.assert200(response)
        else:
            print('  * test_go: No go label found, skipping test...', file=sys.stderr)

    def test_family(self):
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
        else:
            print('  * test_family: No family found, skipping test...', file=sys.stderr)

