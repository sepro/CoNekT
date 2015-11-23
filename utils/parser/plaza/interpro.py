import csv


class Parser:
    def __init__(self):
        self.annotation = {}

    def read_plaza_interpro(self, filename):
        with open(filename) as csvfile:
            reader = csv.DictReader(csvfile, delimiter=';')
            for row in reader:
                gene = row['gene_id']
                domain = {"id": row['motif_id'],
                          "start": row['start'],
                          "stop": row['stop']}

                if gene not in self.annotation.keys():
                    self.annotation[gene] = []

                if domain not in self.annotation[gene]:
                    self.annotation[gene].append(domain)