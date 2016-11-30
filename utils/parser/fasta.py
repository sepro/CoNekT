import sys
import gzip


class Fasta:
    def __init__(self):
        self.sequences = {}

    def remove_subset(self, length):
        """
        Removes a set of sequences and returns those as a subset

        :param length: number of sequences to remove
        :return: Fasta object with the sequences removed from the current one
        """
        output = Fasta()
        keys = list(self.sequences.keys())
        output.sequences = {k: self.sequences[k] for k in keys[:length]}

        self.sequences = {k: self.sequences[k] for k in keys[length:]}

        return output

    def readfile(self, filename, compressed=False, verbose=False):
        """
        Reads a fasta file to the dictionary

        :param filename: file to read
        :param compressed: set to true if reading form a gzipped file
        :param verbose: set to true to get extra debug information printed to STDERR
        """
        if verbose:
            print("Reading FASTA file:" + filename + "...", file=sys.stderr)

        # Initialize variables
        name = ''
        sequence = []
        count = 1

        # open file
        if compressed:
            f = gzip.open(filename, 'rt')
        else:
            f = open(filename, 'r')

        for line in f:
            line = line.rstrip()
            if line.startswith(">"):
                # ignore if first
                if not name == '':
                    self.sequences[name] = ''.join(sequence)
                    count += 1
                name = line.lstrip('>')
                sequence = []
            else:
                sequence.append(line)

        # add last gene
        self.sequences[name] = ''.join(sequence)

        f.close()
        if verbose:
            print("Done! (found ", count, " sequences)", file=sys.stderr)

    def writefile(self, filename):
        """
        writes the sequences back to a fasta file

        :param filename: file to write to
        """
        with open(filename, 'w') as f:
            for k, v in self.sequences.items():
                print(">" + k, file=f)
                print(v, file=f)
