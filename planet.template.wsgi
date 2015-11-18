#!/usr/bin/env python3
import sys

# WSGI configuration
#
# WSGI_PATH = location of the app, should be the same as the base directory of the config file
# WSGI_ENV  = location of the activate_this.py script in the desired virtual environment
WSGI_PATH = 'enter path'
WSGI_ENV = 'enter path to activate_this.py'


sys.path.insert(0, WSGI_PATH)

activator = WSGI_ENV
with open(activator) as f:
    exec(f.read(), {'__file__': activator})

# import the app. Note that it should not run by itself !
from planet import app as application
