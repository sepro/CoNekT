#!/usr/bin/env python3
from planet import app

from planet.models.sequences import Sequence
from planet.models.species import Species
from planet.models.interpro import Interpro
from planet.models.go import GO
from planet.models.gene_families import GeneFamily

from flask.ext.testing import TestCase

import unittest
import sys


class MyTest(TestCase):

    def create_app(self):
        app.config['DEBUG'] = False
        app.config['SQLALCHEMY_ECHO'] = False
        return app

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


if __name__ == '__main__':
    unittest.main()
