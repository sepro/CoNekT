import sys
import json

class HCCA:
    """
    The HCCA class to create clusters from a Rank Based Network

    """
    def __init__(self, step_size=3, hrr_cutoff=50):
        # Settings
        self.hrrCutoff = hrr_cutoff
        self.stepSize = step_size

        # Dicts to store the network
        self.scoreDic = {}
        self.curDic = {}

        # Temp variables
        self.loners = []
        self.clustered = []
        self.clustets = []

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

    def __clustettes(self, lista, clustets, min_size=200):
        """
        Detect islands of nodes smaller than min_size

        :param lista:
        :param clustets:
        :param min_size:
        :return:
        """
        cons = []
        for j in range(len(lista)):
            cons += self.curDic[lista[j]]
        cons = list(set(cons + lista))
        if len(cons) > min_size:
            return
        elif len(cons) == len(lista):
            cons.sort()
            if cons not in clustets:
                clustets.append(cons)
            return
        else:
            self.__clustettes(cons, clustets)

    def __remove_loners(self, min_size=200):
        """
        Removes nodes contained in islands (smaller than min_size) from the analysis

        :param min_size:
        :return:
        """
        print("Detecting loners...", end='')

        notLoners = list(self.curDic.keys())

        node_count = len(self.curDic.keys())

        # Detect nodes forming small islands
        for i in range(len(notLoners)):
            self.__clustettes([notLoners[i]], self.clustets, min_size=min_size)

        # Removes nodes from small islands
        deleted_count = 0
        for i in range(len(self.clustets)):
            for j in range(len(self.clustets[i])):
                deleted_count += 1
                del self.curDic[self.clustets[i][j]]

        print("Done!\nRemoved %d nodes (out of %d)" % (deleted_count, node_count))

    def print_debug(self):
        print("scoreDict:")
        print(json.dumps(self.scoreDic, indent='\t')[:500], "...")

        print("curDict:")
        print(json.dumps(self.curDic, indent='\t')[:500], "...")

        print("loners:")
        print(json.dumps(self.loners, indent='\t')[:500], "...")

    def SurroundingStep(self, lista, whole, step):
        """

        :param lista:
        :param whole:
        :param step:
        :return:
        """
        if step < self.stepSize:  ##step size is defined to 3
            nvn = lista
            for j in range(len(lista)):
                nvn += self.curDic[lista[j]]
            nvn = list(set(nvn))
            self.SurroundingStep(nvn, whole, step + 1)
        else:
            whole.append(lista)

    def Chisel(self, NVN, clusters):
        """
        this function recursively removes nodes from NVN. Only nodes that are connected more to the inside of NVN are retained

        :param NVN:
        :param clusters:
        :return:
        """
        temp = []
        seta = set(NVN)
        for i in range(len(NVN)):
            connections = self.curDic[NVN[i]]
            inside = set(NVN) & set(connections)
            outside = (set(connections) - set(inside))
            inScore = 0
            outScore = 0
            for j in inside:
                inScore += self.scoreDic[NVN[i]][j]
            for j in outside:
                outScore += self.scoreDic[NVN[i]][j]
            if inScore > outScore:
                temp.append(NVN[i])
        if len(temp) == len(seta):
            clusters.append(temp)
            return
        else:
            self.Chisel(temp, clusters)

    def BiggestIsle(self, lista, clusterSet, curSeed):
        """
        sometimes the NVN is split into to islands after chiseling. This function finds the biggest island and keeps it. The smaller island is discarded.

        :param lista:
        :param clusterSet:
        :param curSeed:
        :return:
        """
        temp = []
        for k in range(len(lista)):
            temp += self.scoreDic[lista[k]].keys()
        nodes = set(temp + lista) & clusterSet
        if len(set(nodes)) == len(set(lista)):
            curSeed.append(list(set(nodes)))
            return
        else:
            self.BiggestIsle(list(nodes), clusterSet, curSeed)

    def nonOverlappers(self, clusters):
        """
        This function accepts a list of Stable Putative Clusters and greedily extracts non overlapping
        clusters with highest modularity.

        :param clusters:
        :return:
        """
        rankedClust = []
        for i in range(len(clusters)):
            inScore = 0
            outScore = 0
            for j in range(len(clusters[i])):
                connections = set(self.scoreDic[clusters[i][j]].keys())
                inCons = list(connections & set(clusters[i]))
                outCons = list(connections - set(clusters[i]))
                inScore = 0
                outScore = 0
                for k in range(len(inCons)):
                    inScore += self.scoreDic[clusters[i][j]][inCons[k]]
                for k in range(len(outCons)):
                    outScore += self.scoreDic[clusters[i][j]][outCons[k]]
            rankedClust.append([outScore / inScore, clusters[i]])

        rankedClust.sort()
        BestClust = [rankedClust[0][1]]
        for i in range(len(rankedClust)):
            counter = 0
            for j in range(len(BestClust)):
                if len(set(rankedClust[i][1]) & set(BestClust[j])) > 0:
                    counter += 1
                    break
            if counter == 0 and rankedClust[i][0] < 1:
                BestClust.append(rankedClust[i][1])
        return BestClust

    def networkEditor(self, clustered):
        """
        This function removes nodes in accepted clusters from the current network.

        :param clustered:
        :return:
        """
        connected = []
        clusteredNodes = []
        for i in range(len(clustered)):
            clusteredNodes += clustered[i]
            for j in range(len(clustered[i])):
                connected += self.curDic[clustered[i][j]]
                del self.curDic[clustered[i][j]]
        connections = list(set(connected) - set(clusteredNodes))
        for i in range(len(connections)):
            self.curDic[connections[i]] = list(set(self.curDic[connections[i]]) - set(clusteredNodes))

    def filler(self, LeftOvers):  ##This function assigns nodes that were not clustered by HCCA to clusters they are having highest connectivity to.
        conScoreMat = [[]] * len(self.clustered)
        clustera = []
        print(len(LeftOvers))
        if len(LeftOvers) != 0:
            for i in range(len(LeftOvers)):
                for j in range(len(self.clustered)):
                    connections = list(set(self.scoreDic[LeftOvers[i]].keys()) & set(self.clustered[j]))
                    score = 0
                    for k in range(len(connections)):
                        score += self.scoreDic[LeftOvers[i]][connections[k]]
                    conScoreMat[j] = score

                topScore = max(conScoreMat)
                if topScore != 0:
                    sizeList = []
                    for j in range(len(conScoreMat)):
                        if conScoreMat[j] == topScore:
                            sizeList.append([len(self.clustered[j]), j])
                    sizeList.sort()
                    self.clustered[sizeList[0][1]] += [LeftOvers[i]]
                    clustera.append(LeftOvers[i])
            LeftOvers = list(set(LeftOvers) - set(clustera))
            return self.filler(LeftOvers)
        else:
            return

    def run_iteration(self):
        """
        Run one iteration of CCA

        :return:
        """
        save = []
        notClustered = list(self.curDic.keys())
        for i in range(len(notClustered)):

            sys.stdout.write("\rNode " + str(i) + " out of " + str(len(notClustered)))
            sys.stdout.flush()

            whole = []
            clusters = []
            self.SurroundingStep([notClustered[i]], whole, 0)
            self.Chisel(whole[0], clusters)
            if len(clusters[0]) > 20:
                checked = []
                for j in range(len(clusters[0])):
                    if clusters[0][j] not in checked:
                        curSeed = []
                        self.BiggestIsle([clusters[0][j]], set(clusters[0]), curSeed)
                        checked += curSeed[0]
                        if 200 > len(curSeed[0]) > 40:  ##Here the desired size of clusters is specified
                            save.append(curSeed[0])
                            break
        print("\nfinding non-overlappers")
        newCluster = self.nonOverlappers(save)
        print("Found %s non overlapping SPCs. Making a cluster list" % len(newCluster))
        for i in range(len(newCluster)):
            self.clustered.append(newCluster[i])
        print("%s clusters are now existing. Started the network edit." % len(self.clustered))
        self.networkEditor(newCluster)
        print("finished the edit.")

    def build_clusters(self):
        """
        Function that will build clusters from the current network
        """
        self.__remove_loners()

        iteration = 1

        while True:
            try:
                print("Iteration: %s" % iteration)
                self.run_iteration()
                iteration += 1
            except:
                leftovers = list(self.curDic.keys())

                self.filler(leftovers)
                break

    def write_output(self, filename):
        save = []
        for i in range(len(self.clustered)):
            for j in range(len(self.clustered[i])):
                save.append("%s\t%s\n" % (self.clustered[i][j], str(i)))
        for i in range(len(self.clustets)):
            for j in range(len(self.clustets[i])):
                save.append("%s\ts%s\n" % (self.clustets[i][j], str(i)))
        for i in range(len(self.loners)):
            save.append("%s\ts%s\n" % (self.loners[i], "NA"))

        v = open(filename, "w")
        v.writelines(save)
        v.close()

if __name__ == "__main__":
    hcca_test = HCCA(step_size=3, hrr_cutoff=50)

    hcca_test.read_network(sys.argv[1])

    hcca_test.build_clusters()

    hcca_test.write_output(sys.argv[2])

