import csv


class Parser:
    def __init__(self):
        self.families = {}

    def read(self, filename):
        with open(filename) as csvfile:
            reader = csv.DictReader(csvfile, delimiter=';')
            for row in reader:
                family = row['gf_id']
                genes = row['genes']

                if family not in self.families.keys():
                    self.families[family] = genes.split(',')
