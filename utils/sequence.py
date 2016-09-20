"""
A set of functions to work with biological sequences
"""

# Simple codon table, without degeneration
__CODONTABLE = {'ATA': 'I', 'ATC': 'I', 'ATT': 'I', 'ATG': 'M',
                'ACA': 'T', 'ACC': 'T', 'ACG': 'T', 'ACT': 'T',
                'AAC': 'N', 'AAT': 'N', 'AAA': 'K', 'AAG': 'K',
                'AGC': 'S', 'AGT': 'S', 'AGA': 'R', 'AGG': 'R',
                'CTA': 'L', 'CTC': 'L', 'CTG': 'L', 'CTT': 'L',
                'CCA': 'P', 'CCC': 'P', 'CCG': 'P', 'CCT': 'P',
                'CAC': 'H', 'CAT': 'H', 'CAA': 'Q', 'CAG': 'Q',
                'CGA': 'R', 'CGC': 'R', 'CGG': 'R', 'CGT': 'R',
                'GTA': 'V', 'GTC': 'V', 'GTG': 'V', 'GTT': 'V',
                'GCA': 'A', 'GCC': 'A', 'GCG': 'A', 'GCT': 'A',
                'GAC': 'D', 'GAT': 'D', 'GAA': 'E', 'GAG': 'E',
                'GGA': 'G', 'GGC': 'G', 'GGG': 'G', 'GGT': 'G',
                'TCA': 'S', 'TCC': 'S', 'TCG': 'S', 'TCT': 'S',
                'TTC': 'F', 'TTT': 'F', 'TTA': 'L', 'TTG': 'L',
                'TAC': 'Y', 'TAT': 'Y', 'TAA': '*', 'TAG': '*',
                'TGC': 'C', 'TGT': 'C', 'TGA': '*', 'TGG': 'W'}


def translate(sequence, trim=True, return_on_stop=True):
    """
    Translates a nucleotide (dna) sequence and returns the amino acid sequence

    :param sequence: nucleotide sequence to translate
    :param trim: Start translation at the first start codon (ATG)
    :param return_on_stop: Stops translation at the first stop codon
    :return: translated sequence
    """
    output = ""
    sequence = sequence.upper()
    trimmed_sequence = sequence

    if trim:
        start = sequence.find('ATG')
        trimmed_sequence = trimmed_sequence[start:]

    codons = [trimmed_sequence[i:i+3] for i in range(0, len(trimmed_sequence), 3)]

    for codon in codons:
        if codon in __CODONTABLE:
            output += __CODONTABLE[codon]
            if __CODONTABLE[codon] == '*' and return_on_stop:
                break
        else:
            output += 'X'

    return output
