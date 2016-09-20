from utils.tau import tau

from unittest import TestCase


class UtilsTest(TestCase):
    def test_tau(self):
        self.assertEqual(tau([1, 0, 0, 0, 0, 0]), 1)
        self.assertEqual(tau([1, 1, 1, 1, 1, 1]), 0)
        self.assertEqual("%.2f" % tau([0, 8, 0, 0, 0, 2, 0, 2, 0, 0, 0, 0]), "0.95")  # example from Yanai et al. 2005
