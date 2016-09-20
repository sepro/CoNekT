from utils.tau import tau
from utils.entropy import entropy
from utils.jaccard import jaccard
from utils.sequence import translate

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

    def test_sequence(self):
        sequence = "ATGTCAGAATTATTACAGTTGCCTCCAGGTTTCCGATTTCACCCTACCGATGAAGAGCTTGTCATGCACTATCTCTGCCGCAAATGTGCCTCTCAGTCCATCGCCGTTCCGATCATCGCTGAGATCGATCTCTACAAATACGATCCATGGGAGCTTCCTGGTTTAGCCTTGTATGGTGAGAAGGAATGGTACTTCTTCTCTCCCAGGGACAGAAAATATCCCAACGGTTCGCGTCCTAACCGGTCCGCTGGTTCTGGTTACTGGAAAGCTACCGGAGCTGATAAACCGATCGGACTACCTAAACCGGTCGGAATTAAGAAAGCTCTTGTTTTCTACGCCGGCAAAGCTCCAAAGGGAGAGAAAACCAATTGGATCATGCACGAGTACCGTCTCGCCGACGTTGACCGGTCCGTTCGCAAGAAGAAGAATAGTCTCAGGCTGGATGATTGGGTTCTCTGCCGGATTTACAACAAAAAAGGAGCTACCGAGAGGCGGGGACCACCGCCTCCGGTTGTTTACGGCGACGAAATCATGGAGGAGAAGCCGAAGGTGACGGAGATGGTTATGCCTCCGCCGCCGCAACAGACAAGTGAGTTCGCGTATTTCGACACGTCGGATTCGGTGCCGAAGCTGCATACTACGGATTCGAGTTGCTCGGAGCAGGTGGTGTCGCCGGAGTTCACGAGCGAGGTTCAGAGCGAGCCCAAGTGGAAAGATTGGTCGGCCGTAAGTAATGACAATAACAATACCCTTGATTTTGGGTTTAATTACATTGATGCCACCGTGGATAACGCGTTTGGAGGAGGAGGGAGTAGTAATCAGATGTTTCCGCTACAGGATATGTTCATGTACATGCAGAAGCCTTACTAG"
        translation = "MSELLQLPPGFRFHPTDEELVMHYLCRKCASQSIAVPIIAEIDLYKYDPWELPGLALYGEKEWYFFSPRDRKYPNGSRPNRSAGSGYWKATGADKPIGLPKPVGIKKALVFYAGKAPKGEKTNWIMHEYRLADVDRSVRKKKNSLRLDDWVLCRIYNKKGATERRGPPPPVVYGDEIMEEKPKVTEMVMPPPPQQTSEFAYFDTSDSVPKLHTTDSSCSEQVVSPEFTSEVQSEPKWKDWSAVSNDNNNTLDFGFNYIDATVDNAFGGGGSSNQMFPLQDMFMYMQKPY*"

        self.assertEqual(translate(sequence), translation)
        self.assertEqual(translate(sequence, trim=False), translation)
        self.assertNotEqual(translate("AAA" + sequence, trim=False), translation)
        self.assertEqual(translate("AAA" + sequence, trim=True), translation)
        self.assertNotEqual(translate(sequence+"AAA", return_on_stop=False), translation)
        self.assertEqual(translate(sequence+"AAA", return_on_stop=False), translation + "K")
        self.assertEqual(translate(sequence+"AAA", return_on_stop=True), translation)
        self.assertEqual(translate("ATGSEB"), "MX")
