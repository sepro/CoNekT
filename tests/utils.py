from utils.tau import tau
from utils.entropy import entropy
from utils.jaccard import jaccard

from unittest import TestCase


class UtilsTest(TestCase):
    def test_tau(self):
        self.assertEqual(tau([1, 0, 0, 0, 0, 0]), 1)
        self.assertEqual(tau([1, 1, 1, 1, 1, 1]), 0)
        self.assertEqual("%.2f" % tau([0, 8, 0, 0, 0, 2, 0, 2, 0, 0, 0, 0]), "0.95")  # example from Yanai et al. 2005

    def test_entropy(self):
        self.assertEqual(entropy([1, 0, 0, 0, 0, 0]), 0)

    def test_jaccard(self):
        self.assertEqual(jaccard('ab', 'bc'), 1/3)
        self.assertEqual(jaccard('ab', 'cd'), 0)
        self.assertEqual(jaccard('ab', 'ab'), 1)
