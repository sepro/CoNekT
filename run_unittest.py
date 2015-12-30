#!/usr/bin/env python3
from planet import app

from planet.models.sequences import Sequence

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

            response = self.client.get("/sequence/fasta/protein/%d" % sequence.id)
            self.assert200(response)

            response = self.client.get("/sequence/view/%d" % sequence.id)
            self.assert_template_used('sequence.html')
            self.assert200(response)

            response = self.client.get("/sequence/view/a")
            self.assert404(response)
        else:
            print('  * test_sequence: No sequence found, skipping test...', file=sys.stderr)


if __name__ == '__main__':
    unittest.main()
