import sys

class Fasta:
    def __init__(self):
        self.sequences = {}

    def readfile(self, filename):
        print("Reading FASTA file:" + filename + "...", file=sys.stderr)

        # Initialize variables
        name = ''
        sequence = []
        count = 1

        # open file
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
        print("Done! (found ", count, " sequences)", file=sys.stderr)