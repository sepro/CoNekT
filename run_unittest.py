#!/usr/bin/env python3
from coverage import coverage

cov = coverage(branch=True, omit=['virtualenv/*', 'tests/*', 'config.py', 'utils/benchmark.py'])
cov.start()

import unittest
import os

from tests.website import WebsiteTest
from tests.utils import UtilsTest
from tests.build import BuildTest
from tests.admin import AdminTest

if __name__ == '__main__':
    try:
        unittest.main(failfast=True)
    except:
        pass

    cov.stop()
    cov.save()
    print("\n\nCoverage Report:\n")
    cov.report()
    cov.html_report(directory='tmp/coverage')
    cov.erase()
