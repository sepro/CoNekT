#!/usr/bin/env python3
from planet import create_app, db

from flask import url_for
from flask_testing import TestCase

from .config import LOGIN_ENABLED

import unittest
import json
import os

required_endpoints = ['/admin/add/species/', '/admin/add/expression_profiles/',
                      '/admin/add/coexpression_network/', '/admin/add/coexpression_clusters/',
                      '/admin/add/expression_specificity/', '/admin/add/families/', '/admin/add/go/',
                      '/admin/add/interpro/', '/admin/add/clades/', '/admin/add/xrefs/',
                      '/admin/add/xrefs_families/', '/admin/controls/', '/admin/species/', '/admin/clades/',
                      '/admin/families/', '/admin/networks/', '/admin/clusters/', '/admin/specificity/',
                      '/admin/condition_tissue/', '/admin/add/functional_data/', '/admin/add/sequence_descriptions/',
                      '/admin_controls/update/counts', '/admin_controls/update/clades', '/admin/build/ecc/',
                      '/admin/build/cluster_similarities/', '/admin/build/go_enrichment', '/admin/build/hcca_clusters/',
                      '/admin/build/neighborhood_to_clusters/']


class AdminTest(TestCase):
    """
    BuildCase to check if the build functions work as planned
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
        from planet.models.users import User
        db.create_all()
        test_admin = User('admin', 'admin', '', is_admin=True)
        test_user = User('user', 'user', '', is_admin=False)

        db.session.add(test_admin)
        db.session.add(test_user)
        db.session.commit()

    def tearDown(self):
        """
        Removes test database again, so the next test can start with a clean slate
        """
        db.session.remove()
        db.drop_all()

    @unittest.skipIf(not LOGIN_ENABLED, "Skipping test_admin_views because LOGIN is not enabled")
    def test_admin_views_as_admin(self):
        response = self.client.post('/auth/login', data=dict(username='admin', password='admin', keep_logged='y'),
                                    follow_redirects=True)
        self.assert200(response)
        self.assertTrue('You have successfully logged in.' in response.data.decode('utf-8'))

        for required_endpoint in required_endpoints:
            response = self.client.get(required_endpoint, follow_redirects=True)
            # print(required_endpoint)
            self.assert200(response)

    @unittest.skipIf(not LOGIN_ENABLED, "Skipping test_admin_views because LOGIN is not enabled")
    def test_admin_views_as_anonymous(self):
        # make sure these endpoints cannot be reached without logging in
        for required_endpoint in required_endpoints:
            response = self.client.get(required_endpoint, follow_redirects=True)
            self.assert403(response)

    @unittest.skipIf(not LOGIN_ENABLED, "Skipping test_admin_views because LOGIN is not enabled")
    def test_admin_views_as_user(self):
        response = self.client.post('/auth/login', data=dict(username='user', password='user', keep_logged='y'),
                                    follow_redirects=True)
        self.assert200(response)
        self.assertTrue('You have successfully logged in.' in response.data.decode('utf-8'))

        for required_endpoint in required_endpoints:
            response = self.client.get(required_endpoint, follow_redirects=True)
            self.assert403(response)

    @unittest.skipIf(not LOGIN_ENABLED, "Skipping test_admin_controls because LOGIN is not enabled")
    def test_admin_controls(self):
        # First Log In and Test if this is successful
        response = self.client.post('/auth/login', data=dict(username='admin', password='admin', keep_logged='y'),
                                    follow_redirects=True)
        self.assert200(response)
        self.assertTrue('You have successfully logged in.' in response.data.decode('utf-8'))

        # Add functional data
        with open('./tests/data/test_go.obo', 'rb') as go_data, open('./tests/data/test_interpro.xml', 'rb') as ip_data:
            payload = {'go': go_data,
                       'interpro': ip_data}

            response = self.client.post('/admin_controls/add/functional_data', data=payload, follow_redirects=True,
                                        content_type='multipart/form-data')
            self.assert200(response)
            self.assertTrue('GO data added.' in response.data.decode('utf-8'))  # Check for flash message
            self.assertTrue('InterPro data added.' in response.data.decode('utf-8'))  # Check for flash message

        # Add Species
        with open('./tests/data/mamut.cds.fasta', 'rb') as fasta_data:
            payload = {'code': 'mmu', 'name': 'Marek mutwiliana',
                       'data_type': 'genome', 'color': '#000000',
                       'highlight': '#DDDDDD',
                       'fasta': fasta_data,
                       'description': '**Markdown supported**'}

            response = self.client.post('/admin_controls/add/species', data=payload,
                                        follow_redirects=True, content_type='multipart/form-data')
            self.assert200(response)
            self.assertTrue('Added species' in response.data.decode('utf-8'))  # Check for flash message

        # Add Sequence descriptions
        with open('./tests/data/mamut.descriptions.txt', 'rb') as description_data:
            payload = {'species_id': 1, 'file': description_data}

            response = self.client.post('/admin_controls/add/sequence_descriptions', data=payload,
                                        follow_redirects=True,
                                        content_type='multipart/form-data')
            self.assert200(response)
            self.assertTrue('Added descriptions from file' in response.data.decode('utf-8'))  # Check for flash message

        # Add GO
        with open('./tests/data/functional_data/mamut.go.txt', 'rb') as go_data:
            payload = {'species_id': 1,
                       'source': 'Fake unittest data',
                       'file': go_data}

            response = self.client.post('/admin_controls/add/go', data=payload, follow_redirects=True,
                                        content_type='multipart/form-data')
            self.assert200(response)
            self.assertTrue('Added GO terms from file' in response.data.decode('utf-8'))  # Check for flash message

        # Add InterPro
        with open('./tests/data/functional_data/mamut.interpro.txt', 'rb') as interpro_data:
            payload = {'species_id': 1,
                       'file': interpro_data}

            response = self.client.post('/admin_controls/add/interpro', data=payload, follow_redirects=True,
                                        content_type='multipart/form-data')
            self.assert200(response)
            self.assertTrue('Added InterPro terms from file' in response.data.decode('utf-8'))  # Check for flash message

        # Add Expression Profiles
        with open('./tests/data/expression/mamut.tpm.matrix.txt', 'rb') as matrix_data, \
                open('./tests/data/expression/mamut.expression_annotation.txt', 'rb') as annotation_data, \
                open('./tests/data/expression/mamut.expression_order_color.txt', 'rb') as order_color_data:
            payload = {'species_id': 1,
                       'source': 'lstrap',
                       'matrix_file': matrix_data,
                       'annotation_file': annotation_data,
                       'order_colors_file': order_color_data}

            response = self.client.post('/admin_controls/add/expression_profile', data=payload, follow_redirects=True,
                                        content_type='multipart/form-data')
            self.assert200(response)
            self.assertTrue('Added expression profiles for species' in response.data.decode('utf-8'))  # Check for flash message

        # Add Co-Expression Network
        with open('./tests/data/expression/mamut.pcc.txt', 'rb') as network_data:
            payload = {'species_id': 1,
                       'description': 'fake network for unittests',
                       'limit': 30,
                       'pcc_cutoff': 0.7,
                       'file': network_data}

            response = self.client.post('/admin_controls/add/coexpression_network', data=payload, follow_redirects=True,
                                        content_type='multipart/form-data')
            self.assert200(response)
            self.assertTrue('Added coexpression network for species' in response.data.decode('utf-8'))  # Check for flash message

        # Add Co-Expression Clusters
        with open('./tests/data/expression/mamut.mcl_clusters.txt', 'rb') as cluster_data:
            payload = {'network_id': 1,
                       'description': 'fake clusters for unittests',
                       'min_size': 1,
                       'file': cluster_data}

            response = self.client.post('/admin_controls/add/coexpression_clusters', data=payload, follow_redirects=True,
                                        content_type='multipart/form-data')
            self.assert200(response)
            self.assertTrue(
                'Added coexpression clusters for network method' in response.data.decode('utf-8'))  # Check for flash message

        # Add Specificity
        payload = {'species_id': 1,
                   'description': 'fake specificity for unittests'}

        response = self.client.post('/admin_controls/add/condition_specificity', data=payload, follow_redirects=True)
        self.assert200(response)
        self.assertTrue('Calculated condition specificities for species' in response.data.decode('utf-8'))  # Check for flash message

        # Add Clades
        payload = {'clades_json': json.dumps({"Marek mutwiliana": {"species": ["mmu"], "tree": None}})}

        response = self.client.post('/admin_controls/add/clades', data=payload, follow_redirects=True)
        self.assert200(response)
        self.assertTrue('Added clades' in response.data.decode('utf-8'))  # Check for flash message

        # Add MCL families
        with open('./tests/data/comparative_data/mamut.families.mcl.txt', 'rb') as mcl_data:
            payload = {
                'method_description': 'Fake MCL families',
                'source': 'mcl',
                'file': mcl_data
            }

            response = self.client.post('/admin_controls/add/family', data=payload, follow_redirects=True)
            self.assert200(response)
            self.assertTrue('Added Gene families from file' in response.data.decode('utf-8'))  # Check for flash message

        # Add OrthoFinder families
        with open('./tests/data/comparative_data/mamut.families.orthofinder.txt', 'rb') as of_data:
            payload = {
                'method_description': 'Fake OrthoFinder families',
                'source': 'orthofinder',
                'file': of_data
            }

            response = self.client.post('/admin_controls/add/family', data=payload, follow_redirects=True)
            self.assert200(response)
            self.assertTrue('Added Gene families from file' in response.data.decode('utf-8'))  # Check for flash message

        # Add Xrefs to sequences
        with open('./tests/data/mamut.xref.txt', 'rb') as xref_data:
            payload = {
                'species_id': 1,
                'platforms': 'custom',
                'file': xref_data
            }

            response = self.client.post('/admin_controls/add/xrefs', data=payload, follow_redirects=True)
            self.assert200(response)
            self.assertTrue('Added XRefs from file' in response.data.decode('utf-8'))  # Check for flash message

        # Updates, ...
        response = self.client.get('/admin_controls/update/counts', follow_redirects=True)
        self.assert200(response)
        self.assertTrue('CoexpressionClusteringMethod count updated' in response.data.decode('utf-8'))  # Check for flash message
        self.assertTrue('ExpressionNetworkMethod counts updated' in response.data.decode('utf-8'))  # Check for flash message
        self.assertTrue('GeneFamilyMethod count updated' in response.data.decode('utf-8'))  # Check for flash message
        self.assertTrue('Species count updated' in response.data.decode('utf-8'))  # Check for flash message
        self.assertTrue('GO count updated' in response.data.decode('utf-8'))  # Check for flash message

        response = self.client.get('/admin_controls/calculate_enrichment', follow_redirects=True)
        self.assert200(response)
        self.assertTrue('Successfully calculated GO enrichment' in response.data.decode('utf-8'))  # Check for flash message

        response = self.client.get('/admin_controls/clear/cache', follow_redirects=True)
        self.assert200(response)
        self.assertTrue('Cache cleared' in response.data.decode('utf-8'))  # Check for flash message

        response = self.client.get('/admin_controls/update/clades', follow_redirects=True)
        self.assert200(response)
        self.assertTrue('All clades updated' in response.data.decode('utf-8'))  # Check for flash message

        response = self.client.get('/admin_controls/update/clades', follow_redirects=True)
        self.assert200(response)
        self.assertTrue('All clades updated' in response.data.decode('utf-8'))  # Check for flash message

        response = self.client.get('/admin_controls/export_ftp', follow_redirects=True)
        self.assert200(response)
        self.assertTrue('Successfully exported data to FTP folder' in response.data.decode('utf-8'))  # Check for flash message

        required_files = ['sequences/mmu.aa.fasta.gz', 'sequences/mmu.cds.fasta.gz', 'annotation/mmu.go.csv.gz',
                          'annotation/mmu.interpro.csv.gz', 'expression/clustering_method_1.tab',
                          'expression/clustering_methods_overview.txt', 'expression/network_method_1.tab.gz',
                          'expression/network_methods_overview.txt', 'families/families_method_1.tab',
                          'families/families_method_2.tab', 'families/methods_overview.txt']

        for rf in required_files:
            path = os.path.join(self.app.config['PLANET_FTP_DATA'], rf)
            self.assertTrue(os.path.isfile(path))


