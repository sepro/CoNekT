"""
Parser class for interpro.xml: xml file from EBI with the info on all InterPro Domains
"""
class InterPro:
    def __init__(self):
        self.id = ''
        self.label = ''
        self.description = ''

    def set_id(self, id):
        self.id = id

    def set_label(self, label):
        self.label = label

    def set_description(self, description):
        self.description = description

class Parser:
    """
    reads the specified InterPro
    """
    def __init__(self):
        self.domains = []

    def readfile(self, filename):
        """
        function that reads the file and stores the data in memory
        """
        pass
