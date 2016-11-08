"""
Parser class for interpro.xml: xml file from EBI with the info on all InterPro Domains
"""
import xml.etree.ElementTree as ET
import csv

class InterPro:
    def __init__(self):
        self.label = ''
        self.description = ''

    def set_label(self, label):
        self.label = label

    def set_description(self, description):
        self.description = description

    def print(self):
        print(self.label, self.description)


class Parser:
    """
    reads the specified InterPro
    """
    def __init__(self):
        self.domains = []

    def print(self):
        for domain in self.domains:
            domain.print()

    def readfile(self, filename):
        """
        function that reads the file and stores the data in memory
        """
        e = ET.parse(filename).getroot()

        for domain in e.findall('interpro'):
            new_domain = InterPro()

            new_domain.set_label(domain.get('id'))
            new_domain.set_description(domain.get('short_name'))

            self.domains.append(new_domain)


class DomainParser:
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

    def read_interproscan(self, filename):
        with open(filename, "r") as f:
            for line in f:
                parts = line.split('\t')
                if len(parts) > 11:
                    gene = parts[0]
                    domain = {"id": parts[11],
                              "start": int(parts[6]),
                              "stop": int(parts[7])}

                    if gene not in self.annotation.keys():
                        self.annotation[gene] = []

                    if domain not in self.annotation[gene]:
                        self.annotation[gene].append(domain)