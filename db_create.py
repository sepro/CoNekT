#!/usr/bin/env python3
"""

Script to create the initial database and migration information

"""
from migrate.versioning import api

from config import SQLALCHEMY_DATABASE_URI
from config import SQLALCHEMY_MIGRATE_REPO
from config import UPLOAD_FOLDER
from config import ADMIN_PASSWORD
from config import ADMIN_EMAIL

from planet import app, db
from planet.models.users import User


import os.path

db.create_all(app=app)

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
    print("\nThe upload folder has been created")

if not os.path.exists(SQLALCHEMY_MIGRATE_REPO):
    api.create(SQLALCHEMY_MIGRATE_REPO, 'database repository')
    api.version_control(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO)
else:
    api.version_control(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO, api.version(SQLALCHEMY_MIGRATE_REPO))


# If there are no users in the database create an admin account
if len(User.query.all()) == 0:
    db.session.add(User("admin", ADMIN_PASSWORD, ADMIN_EMAIL, is_admin=True))
    db.session.commit()

    print("\nAn admin account has been created. Username=\'admin\' and password=\'" + ADMIN_PASSWORD + "\'")
    print("IMPORTANT: Change the password for this account")