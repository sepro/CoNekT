import csv


class Parser:
    def __init__(self):
        self.annotation = {}

    def read_plaza_go(self, filename):
        with open(filename) as csvfile:
            reader = csv.DictReader(csvfile, delimiter=';')
            for row in reader:
                gene = row['gene_id']
                go = {"id": row['go'],
                      "evidence": row['evidence'],
                      "source": row['provider'] if 'provider' in row.keys() else 'PLAZA'}

                if gene not in self.annotation.keys():
                    self.annotation[gene] = []

                if go not in self.annotation[gene]:
                    self.annotation[gene].append(go)
