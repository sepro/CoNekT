import sys
import json

class HCCA:
    """
    The HCCA class to create clusters from a Rank Based Network

    """
    def __init__(self, step_size=3, hrr_cutoff=50, min_cluster_size=40, max_cluster_size=200):
        """
        Clear lists and store settings

        :param step_size: desired step size
        :param hrr_cutoff: desired hrr_cutoff
        :param min_cluster_size: minimal size of a cluster
        :param max_cluster_size: maximal size of a cluster
        """
        # Settings
        self.hrrCutoff = hrr_cutoff
        self.stepSize = step_size

        self.min_cluster_size = min_cluster_size
        self.max_cluster_size = max_cluster_size

        # Dicts to store the network
        self.scoreDic = {}
        self.curDic = {}

        # Temp variables
        self.loners = []
        self.clustered = []
        self.clustets = []

    def __clustettes(self, nodes):
        """
        Detect islands of nodes smaller than max_cluster_size

        :param nodes:
        :return:
        """
        cons = []

        for l in nodes:
            cons += self.curDic[l]

        cons = list(set(cons + nodes))

        # If the network is larger than the max_cluster size it is not a clustet, skip
        if len(cons) <= self.max_cluster_size:
            if len(cons) == len(nodes):
                cons.sort()
                if cons not in self.clustets:
                    self.clustets.append(cons)
            else:
                self.__clustettes(cons)

    def __remove_loners(self):
        """
        Removes nodes contained in islands (smaller than min_size) from the analysis
        """
        print("Detecting loners...", end='')

        node_count = len(self.curDic)

        # Detect nodes forming small islands
        for node in self.curDic.keys():
            self.__clustettes([node])

        # Removes nodes from small islands
        deleted_count = 0
        for clustet in self.clustets:
            for c in clustet:
                del self.curDic[c]
                deleted_count += 1

        print("Done!\nFound %d loners (out of %d nodes)" % (deleted_count, node_count))

    def __surrounding_step(self, node_list, whole, step):
        """

        :param node_list:
        :param whole:
        :param step:
        :return:
        """
        if step < self.stepSize:
            nvn = [l for l in node_list]
            for l in node_list:
                nvn += self.curDic[l]

            nvn = list(set(nvn))

            self.__surrounding_step(nvn, whole, step + 1)
        else:
            whole.append(node_list)

    def __chisel(self, nvn, clusters):
        """
        this function recursively removes nodes from NVN. Only nodes that are connected more to the inside of NVN are retained

        :param nvn:
        :param clusters:
        :return:
        """
        temp = []
        seta = set(nvn)

        for n in nvn:
            connections = self.curDic[n]

            inside = set(nvn) & set(connections)
            outside = (set(connections) - set(inside))
            in_score = 0
            out_score = 0
            for j in inside:
                in_score += self.scoreDic[n][j]
            for j in outside:
                out_score += self.scoreDic[n][j]
            if in_score > out_score:
                temp.append(n)

        if len(temp) == len(seta):
            clusters.append(temp)
        else:
            self.__chisel(temp, clusters)

    def __biggest_isle(self, lista, cluster_set, cur_seed):
        """
        Sometimes the NVN is split into to islands after chiseling. This function finds the biggest island
        and keeps it. The smaller island is discarded.

        :param lista:
        :param cluster_set:
        :param cur_seed:
        :return:
        """
        temp = []
        for k in range(len(lista)):
            temp += self.scoreDic[lista[k]].keys()
        nodes = set(temp + lista) & cluster_set
        if len(set(nodes)) == len(set(lista)):
            cur_seed.append(list(set(nodes)))
        else:
            self.__biggest_isle(list(nodes), cluster_set, cur_seed)

    def __find_non_overlapping(self, clusters):
        """
        This function accepts a list of Stable Putative Clusters and greedily extracts non overlapping
        clusters with highest modularity.

        :param clusters:
        :return:
        """
        ranked_clust = []
        for cluster in clusters:
            in_score = 0
            out_score = 0
            for node in cluster:
                connections = set(self.scoreDic[node].keys())
                in_cons = list(connections & set(cluster))
                out_cons = list(connections - set(cluster))
                in_score = 0
                out_score = 0

                for in_con in in_cons:
                    in_score += self.scoreDic[node][in_con]

                for out_con in out_cons:
                    out_score += self.scoreDic[node][out_con]

            ranked_clust.append([out_score / in_score, cluster])

        ranked_clust.sort()
        best_clust = [ranked_clust[0][1]]
        for i in range(len(ranked_clust)):
            counter = 0
            for j in range(len(best_clust)):
                if len(set(ranked_clust[i][1]) & set(best_clust[j])) > 0:
                    counter += 1
                    break
            if counter == 0 and ranked_clust[i][0] < 1:
                best_clust.append(ranked_clust[i][1])
        return best_clust

    def __network_editor(self, clustered):
        """
        This function removes nodes in accepted clusters from the current network.

        :param clustered:
        """
        connected = []
        clustered_nodes = []
        for i in range(len(clustered)):
            clustered_nodes += clustered[i]
            for j in range(len(clustered[i])):
                connected += self.curDic[clustered[i][j]]
                del self.curDic[clustered[i][j]]
        connections = list(set(connected) - set(clustered_nodes))
        for i in range(len(connections)):
            self.curDic[connections[i]] = list(set(self.curDic[connections[i]]) - set(clustered_nodes))

    def __filler(self, left_overs):
        """
        This function assigns nodes that were not clustered by HCCA to clusters they are having highest connectivity to.

        :param left_overs:
        :return:
        """
        con_score_mat = [[]] * len(self.clustered)
        clustera = []
        print("Leftovers : %d" % len(left_overs))
        if len(left_overs) != 0:
            for i in range(len(left_overs)):
                for j in range(len(self.clustered)):
                    connections = list(set(self.scoreDic[left_overs[i]].keys()) & set(self.clustered[j]))
                    score = 0
                    for k in range(len(connections)):
                        score += self.scoreDic[left_overs[i]][connections[k]]
                    con_score_mat[j] = score

                top_score = max(con_score_mat)
                if top_score != 0:
                    size_list = []
                    for j in range(len(con_score_mat)):
                        if con_score_mat[j] == top_score:
                            size_list.append([len(self.clustered[j]), j])
                    size_list.sort()
                    self.clustered[size_list[0][1]] += [left_overs[i]]
                    clustera.append(left_overs[i])
            left_overs = list(set(left_overs) - set(clustera))
            self.__filler(left_overs)

    def __iterate(self):
        """
        Runs one iteration of CCA

        :return:
        """
        save = []
        not_clustered = list(self.curDic.keys())
        for i in range(len(not_clustered)):

            sys.stdout.write("\rNode " + str(i) + " out of " + str(len(not_clustered)))
            sys.stdout.flush()

            whole = []
            clusters = []
            self.__surrounding_step([not_clustered[i]], whole, 0)
            self.__chisel(whole[0], clusters)
            if len(clusters[0]) > 20:
                checked = []
                for j in range(len(clusters[0])):
                    if clusters[0][j] not in checked:
                        cur_seed = []
                        self.__biggest_isle([clusters[0][j]], set(clusters[0]), cur_seed)
                        checked += cur_seed[0]
                        # Check if cluster is withing the desired size range
                        if self.max_cluster_size > len(cur_seed[0]) > self.min_cluster_size:
                            save.append(cur_seed[0])
                            break

        print("\nFinding non-overlappers...", end='')
        new_cluster = self.__find_non_overlapping(save)
        print("Done!\nFound %s non overlapping SPCs. Making a cluster list..." % len(new_cluster), end='')
        for i in range(len(new_cluster)):
            self.clustered.append(new_cluster[i])

        print("Done!\n\nCurrent number of clusters %d. Starting the network edit..." % len(self.clustered))
        self.__network_editor(new_cluster)
        print("Done!\nFinished the edits.")

    def build_clusters(self):
        """
        Function that will build clusters from the current network
        """
        self.__remove_loners()

        iteration = 1

        while True:
            try:
                print("\n-------------")
                print("Iteration: %s" % iteration)
                print("-------------")

                self.__iterate()

                iteration += 1
            except IndexError:
                # When no additional clusters can be found, and IndexError (out of range) is produced.
                # Catch and handle gracefully
                leftovers = list(self.curDic.keys())

                print("\nClustering completed, handling left overs...")
                self.__filler(leftovers)
                break

    def read_network(self, filename):
        """
        Function to read network from PlaNet 1 HRR files (retained for testing !)

        :param filename: path to file to read
        """
        print("Reading Rank Based network from HRR file...", end='')

        a = open(filename).readlines()  # open network file

        for i in range(len(a)):         # this loop processess the network file into 2 dicts (curDic and scoreDic).
            splitted = a[i].split("\t")
            dicto = {}
            connections = []
            for j in range(5, len(splitted)):
                if "+" in splitted[j]:
                    splitx = splitted[j].split("+")
                    if float(splitx[1]) < self.hrrCutoff:
                        dicto[splitx[0]] = 1 / (float(splitx[1]) + 1)
                        connections.append(splitx[0])
            if len(dicto) != 0:
                self.scoreDic[str(i)] = dicto
                self.curDic[str(i)] = connections
            else:
                self.loners.append(str(i))

        print("Done!")

    def load_data(self, data):
        """
        Loads curDict and scoreDict from dictionary

        {
            "GeneA": {
                "GeneB" : 1 (rank),
                "GeneC" : 2,
                ...
            },
            "GeneB": {
                "GeneA" : 1,
                ...
            },
            ...
        }

        :param data: dictionary with co-expressed pairs and their ranks
        :return:
        """
        print("Loading network from dict...", sep='')

        self.curDic = {}
        self.scoreDic = {}
        self.loners = []

        for gene, scores in data.items():
            neighbors = [k for k, score in scores.items() if score < self.hrrCutoff]
            if len(neighbors) == 0:
                self.loners.append(gene)
            else:
                self.curDic[gene] = neighbors

        for gene, scores in data.items():
            self.scoreDic[gene] = {k: 1/(score + 1) for k, score in scores.items() if score < self.hrrCutoff}

        print("Done!")

    @property
    def clusters(self):
        """
        Returns a list of all members of clusters and clustets, with a name for the cluster/clustet.

        :return: List of tuples [(member, clustername, clustet (bool)), ...]
        """
        output = []
        count = 1
        for cluster in self.clustered:
            for member in cluster:
                output.append((member, "Cluster_%d" % count, False))
            count += 1

        for clustet in self.clustets:
            for member in clustet:
                output.append((member, "Cluster_%d" % count, True))
            count += 1

        return output

    def write_output(self, filename):
        save = []

        for i, cluster in enumerate(self.clustered):
            for member in cluster:
                save.append("%s\t%d\n" % (member, i))

        for i, clustet in enumerate(self.clustets):
            for member in clustet:
                save.append("%s\ts%d\n" % (member, i))

        for loner in self.loners:
            save.append("%s\tsNA\n" % loner)

        # Write output to file
        with open(filename, "w") as v:
            v.writelines(save)

if __name__ == "__main__":
    hcca_test = HCCA(step_size=3, hrr_cutoff=30)

    hcca_test.read_network(sys.argv[1])

    hcca_test.build_clusters()

    hcca_test.write_output(sys.argv[2])

    print(hcca_test.clusters)



