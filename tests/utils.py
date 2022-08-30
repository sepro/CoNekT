from utils.tau import tau
from utils.entropy import entropy, entropy_from_values
from utils.jaccard import jaccard
from utils.sequence import translate
from utils.enrichment import hypergeo_cdf, hypergeo_sf, fdr_correction
from utils.expression import max_spm

from unittest import TestCase


class UtilsTest(TestCase):
    def test_tau(self):
        self.assertEqual(tau([1, 0, 0, 0, 0, 0]), 1)
        self.assertEqual(tau([1, 1, 1, 1, 1, 1]), 0)
        self.assertEqual(tau([0, 0, 0, 0, 0, 0]), None)
        self.assertAlmostEqual(
            tau([0, 8, 0, 0, 0, 2, 0, 2, 0, 0, 0, 0]), 0.95, places=2
        )  # example from Yanai et al. 2005

    def test_enrichment(self):
        self.assertAlmostEqual(hypergeo_cdf(2, 3, 10, 100), 0.999, places=3)
        self.assertAlmostEqual(hypergeo_cdf(2, 6, 10, 100), 0.987, places=3)

        self.assertAlmostEqual(hypergeo_sf(2, 3, 10, 100), 0.026, places=3)
        self.assertAlmostEqual(hypergeo_sf(2, 6, 10, 100), 0.109, places=3)

        self.assertEqual(fdr_correction([0.05, 0.06, 0.07]), [0.07, 0.07, 0.07])

    def test_entropy(self):
        self.assertEqual(entropy([1, 0, 0, 0, 0, 0]), 0)

        self.assertEqual(
            entropy_from_values([0, 0, 0, 1, 1, 1, 2, 2, 2, 3, 3, 3], num_bins=4),
            entropy([3, 3, 3, 3]),
        )
        self.assertEqual(entropy_from_values([0, 0, 0], num_bins=4), entropy([]))

    def test_expression(self):
        self.assertEqual(
            max_spm({"leaf": 1, "root": 0}, substract_background=False),
            {"condition": "leaf", "score": 1},
        )
        self.assertEqual(
            max_spm({"leaf": 1.1, "root": 0.1}, substract_background=True),
            {"condition": "leaf", "score": 1},
        )
        self.assertEqual(max_spm({}, substract_background=False), None)

    def test_jaccard(self):
        self.assertEqual(jaccard("ab", "bc"), 1 / 3)
        self.assertEqual(jaccard("ab", "cd"), 0)
        self.assertEqual(jaccard("ab", "ab"), 1)

    def test_sequence(self):
        sequence = "ATGTCAGAATTATTACAGTTGCCTCCAGGTTTCCGATTTCACCCTACCGATGAAGAGCTTGTCATGCACTATCTCTGCCGCAAATGTGCCTCTCAGTCCATCGCCGTTCCGATCATCGCTGAGATCGATCTCTACAAATACGATCCATGGGAGCTTCCTGGTTTAGCCTTGTATGGTGAGAAGGAATGGTACTTCTTCTCTCCCAGGGACAGAAAATATCCCAACGGTTCGCGTCCTAACCGGTCCGCTGGTTCTGGTTACTGGAAAGCTACCGGAGCTGATAAACCGATCGGACTACCTAAACCGGTCGGAATTAAGAAAGCTCTTGTTTTCTACGCCGGCAAAGCTCCAAAGGGAGAGAAAACCAATTGGATCATGCACGAGTACCGTCTCGCCGACGTTGACCGGTCCGTTCGCAAGAAGAAGAATAGTCTCAGGCTGGATGATTGGGTTCTCTGCCGGATTTACAACAAAAAAGGAGCTACCGAGAGGCGGGGACCACCGCCTCCGGTTGTTTACGGCGACGAAATCATGGAGGAGAAGCCGAAGGTGACGGAGATGGTTATGCCTCCGCCGCCGCAACAGACAAGTGAGTTCGCGTATTTCGACACGTCGGATTCGGTGCCGAAGCTGCATACTACGGATTCGAGTTGCTCGGAGCAGGTGGTGTCGCCGGAGTTCACGAGCGAGGTTCAGAGCGAGCCCAAGTGGAAAGATTGGTCGGCCGTAAGTAATGACAATAACAATACCCTTGATTTTGGGTTTAATTACATTGATGCCACCGTGGATAACGCGTTTGGAGGAGGAGGGAGTAGTAATCAGATGTTTCCGCTACAGGATATGTTCATGTACATGCAGAAGCCTTACTAG"
        translation = "MSELLQLPPGFRFHPTDEELVMHYLCRKCASQSIAVPIIAEIDLYKYDPWELPGLALYGEKEWYFFSPRDRKYPNGSRPNRSAGSGYWKATGADKPIGLPKPVGIKKALVFYAGKAPKGEKTNWIMHEYRLADVDRSVRKKKNSLRLDDWVLCRIYNKKGATERRGPPPPVVYGDEIMEEKPKVTEMVMPPPPQQTSEFAYFDTSDSVPKLHTTDSSCSEQVVSPEFTSEVQSEPKWKDWSAVSNDNNNTLDFGFNYIDATVDNAFGGGGSSNQMFPLQDMFMYMQKPY*"

        self.assertEqual(translate(sequence), translation)
        self.assertEqual(translate(sequence, trim=False), translation)
        self.assertNotEqual(translate("AAA" + sequence, trim=False), translation)
        self.assertEqual(translate("AAA" + sequence, trim=True), translation)
        self.assertNotEqual(
            translate(sequence + "AAA", return_on_stop=False), translation
        )
        self.assertEqual(
            translate(sequence + "AAA", return_on_stop=False), translation + "K"
        )
        self.assertEqual(translate(sequence + "AAA", return_on_stop=True), translation)
        self.assertEqual(translate("ATGSEB"), "MX")
