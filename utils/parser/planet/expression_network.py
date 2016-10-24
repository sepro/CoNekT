import csv


class Parser:
    def __init__(self, ):
        self.network = {}

    def read_expression_network(self, network_file, score_cutoff=30):
        """
        Reads hrr file from the original PlaNet pipeline

        ids are based on line number starting with 0 !

        :param network_file: path to the file with the network (hrr)
        :param score_cutoff: only links with a score equal or better than this value will be included
        :return:
        """
        id_to_probe = {}

        with open(network_file) as csvfile:
            reader = csv.reader(csvfile, delimiter='\t')
            for probe_id, parts in enumerate(reader):

                # probe_id in this case is the line number (starting from zero), parts is a list of all the columns.
                # The columns at index 5 and beyond are the links (line number+score)

                probe = parts[0]
                gene_id = parts[1]
                links = parts[5:]

                id_to_probe[probe_id] = probe

                # add a gene to the network with no links/edges
                self.network[probe] = {"probe_name": probe,
                                       "gene_name": gene_id,
                                       "linked_probes": []}

                # read the edges, probe_names and gene_names cannot be added at this point as
                # the file hasn't been read completely
                for link in links:
                    linked_id, link_score = link.split('+')
                    if int(link_score) <= score_cutoff:
                        new_link = {"link_id": int(linked_id),
                                    "probe_name": "",
                                    "gene_name": "",
                                    "link_score": int(link_score)}
                        self.network[probe]["linked_probes"].append(new_link)

        # Now the id_to_probe table is competed, add missing information and remove line number identifiers
        for probe in self.network.values():
            for linked_probe in probe["linked_probes"]:
                linked_probe["probe_name"] = id_to_probe[linked_probe["link_id"]]
                linked_probe["gene_name"] = self.network[linked_probe["probe_name"]]["gene_name"]
                linked_probe.pop("link_id", None)


