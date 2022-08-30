#!/usr/bin/env python3
import unittest
import os

from tests.website import WebsiteTest
from tests.utils import UtilsTest
from tests.build import BuildTest
from tests.admin import AdminTest

if __name__ == "__main__":
    try:
        unittest.main(failfast=True)
    except:
        pass
