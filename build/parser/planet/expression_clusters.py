import csv


class Parser:
    def __init__(self, ):
        self.clusters = {}

    def read_expression_clusters(self, network_file, cluster_file):
        """
        Reads hrr and hcca file from the original PlaNet pipeline

        ids are based on line number starting with 0 !

        :param network_file: path to the file with the network (hrr)
        :param cluster_file: path to the file with the clusters (hcca)
        :return:
        """
        id_to_probe = {}

        # the network file is required for the mapping from numeric ids to gene ids
        with open(network_file) as csvfile:
            reader = csv.reader(csvfile, delimiter='\t')
            for probe_id, parts in enumerate(reader):
                # probe_id in this case is the line number (starting from zero)

                probe = parts[0]
                gene_id = parts[1]

                id_to_probe[probe_id] = {}
                id_to_probe[probe_id]['probe'] = probe
                id_to_probe[probe_id]['gene'] = gene_id

        with open(cluster_file) as csvfile:
            reader = csv.reader(csvfile, delimiter='\t')
            for parts in reader:
                probe_id = int(parts[0])
                cluster_id = parts[1]

                if cluster_id not in self.clusters:
                    self.clusters[cluster_id] = []

                if probe_id in id_to_probe.keys():
                    self.clusters[cluster_id].append({'probe': id_to_probe[probe_id]['probe'],
                                                      'gene': id_to_probe[probe_id]['gene']})
