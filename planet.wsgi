#!/usr/bin/env python3

from config import WSGI_PATH, WSGI_ENV

import sys
sys.path.insert(0, WSGI_PATH)

activator = WSGI_ENV
with open(activator) as f:
    exec(f.read(), {'__file__': activator})

# import the app. Note that it should not run by itself !
from planet import app as application
