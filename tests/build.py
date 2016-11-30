#!/usr/bin/env python3
from planet import create_app, db

from flask_testing import TestCase


class BuildTest(TestCase):
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

    def tearDown(self):
        """
        Removes test database again, so the next test can start with a clean slate
        """
        db.session.remove()
        db.drop_all()

    def test_build(self):
        from planet.models.species import Species
        from planet.models.sequences import Sequence

        from planet.models.xrefs import XRef
        from planet.models.go import GO
        from planet.models.interpro import Interpro

        Species.add('mmu', 'Marek mutwiliana')
        s = Species.query.first()

        Sequence.add_from_fasta('./tests/data/mamut.cds.fasta', s.id)
        XRef.add_xref_genes_from_file(s.id, './tests/data/mamut.xref.txt')
        GO.add_from_obo('./tests/data/test_go.obo')
        GO.add_go_from_tab('./tests/data/functional_data/mamut.go.txt', s.id, source="Fake UnitTest Data")

        Interpro.add_from_xml('./tests/data/test_interpro.xml')
        Interpro.add_interpro_from_interproscan('./tests/data/functional_data/mamut.interpro.txt', s.id)

        test_sequences = Sequence.query.all()
        test_sequence = Sequence.query.filter_by(name='Gene01').first()
        test_xref = test_sequence.xrefs[0]
        test_go = test_sequence.go_labels.first()
        test_go_association = test_sequence.go_associations.filter_by(evidence=None).first()

        test_interpro = test_sequence.interpro_domains.filter_by(label='IPR000001').first()

        self.assertTrue(len(test_sequences) == 3)                       # Check if all genes are added

        self.assertTrue(test_sequence.name == 'Gene01')
        self.assertTrue(test_sequence.species_id == s.id)

        self.assertTrue(test_sequence.aliases == 'BRCA2')               # Check if alias is added and correct
        self.assertTrue('www.ensembl.org' in test_xref.url)             # Check if url is added
        self.assertTrue(test_xref.platform == 'Ensembl')                # Check if platform is added
        self.assertTrue(test_xref.name == 'BRCA2')                      # Check if platform is added

        self.assertTrue(test_go.label == 'GO:0000003')                  # Check if go is added
        self.assertTrue(test_go.description == '"Third label"')         # Check if go description is parsed
        self.assertTrue(test_go_association.go.label == 'GO:0000001')   # Check if go parent is added

        self.assertTrue(test_interpro.label == 'IPR000001')             # Check if Interpro domain is added
        self.assertTrue('Kringle' in test_interpro.description)        # Check if description is added

