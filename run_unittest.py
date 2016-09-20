#!/usr/bin/env python3
from coverage import coverage

cov = coverage(branch=True, omit=['virtualenv/*', 'tests/*'])
cov.start()

import unittest
import os

from tests.website import WebsiteTest
from tests.utils import UtilsTest

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
