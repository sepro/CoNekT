#!/usr/bin/env python3
from planet import create_app, db

from flask_testing import TestCase

from .config import LOGIN_ENABLED

import unittest
import json

required_endpoints = ['/admin/add/species/', '/admin/add/expression_profiles/',
                      '/admin/add/coexpression_network/', '/admin/add/coexpression_clusters/',
                      '/admin/add/expression_specificity/', '/admin/add/families/', '/admin/add/go/',
                      '/admin/add/interpro/', '/admin/add/clades/', '/admin/add/xrefs/',
                      '/admin/add/xrefs_families/', '/admin/controls/', '/admin/species/', '/admin/clades/',
                      '/admin/families/', '/admin/networks/', '/admin/clusters/', '/admin/specificity/',
                      '/admin/condition_tissue/', '/admin/add/functional_data/']


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

    def test_admin_controls(self):
        # First Log In and Test if this is successfull
        response = self.client.post('/auth/login', data=dict(username='admin', password='admin', keep_logged='y'),
                                    follow_redirects=True)
        self.assert200(response)
        self.assertTrue('You have successfully logged in.' in response.data.decode('utf-8'))
