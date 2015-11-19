"""
Parser class for interpro.xml: xml file from EBI with the info on all InterPro Domains
"""
import xml.etree.ElementTree as ET


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
