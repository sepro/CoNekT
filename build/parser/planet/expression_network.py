import csv


class Parser:
    def __init__(self, ):
        self.network = {}

    def read_expression_network(self, network_file):
        """
        Reads hrr file from the original PlaNet pipeline

        ids are based on line number starting with 0 !

        :param network_file:
        :return:
        """
        id_to_probe = {}

        with open(network_file) as csvfile:
            reader = csv.reader(csvfile, delimiter='\t')
            for probe_id, parts in enumerate(reader):

                probe = parts[0]
                gene_id = parts[1]
                links = parts[5:]

                id_to_probe[probe_id] = probe

                self.network[probe] = {"probe_name": probe,
                                       "gene_name": gene_id,
                                       "linked_probes": []}

                for link in links:
                    linked_id, link_score = link.split('+')
                    new_link = {"link_id": int(linked_id),
                                "probe_name": "",
                                "gene_name": "",
                                "link_score": int(link_score)}
                    self.network[probe]["linked_probes"].append(new_link)

        # Now the id_to_probe table is competed add missing information
        for probe in self.network.values():
            for linked_probe in probe["linked_probes"]:
                linked_probe["probe_name"] = id_to_probe[linked_probe["link_id"]]
                linked_probe["gene_name"] = self.network[linked_probe["probe_name"]]["gene_name"]
                linked_probe.pop("link_id", None)

