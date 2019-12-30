import numpy as np

class Edge(object):
    def __init__(self):
        pass

class Cartesian(Edge):
    def __init__(self, domain ,node=None):
        self.domain = domain
        if node is not None:
            self.node = node
            self.generateEdge()

    def generateEdge(self):
        nodes = self.node.nodes
        self.edges = []
        self.edges.extend([{"node1":i, 
                            "node2": nodes[i]["nextnode"]["f"], 
                            "position": nodes[i]["position"] if nodes[i]["position"][0] == "b" else "b" + str(nodes[i]["position"][1:])
                            }
                            for i in range(len(nodes)) if "f" in nodes[i]["nextnode"]])
        self.edges.extend([{"node1":i, "node2": nodes[i]["nextnode"]["r"], "position": "in"} for i in range(len(nodes)) if "r" in nodes[i]["nextnode"]])
        self.edges.extend([{"node1":i, "node2": nodes[i]["nextnode"]["u"], "position": "in"} for i in range(len(nodes)) if "u" in nodes[i]["nextnode"]])
        self.edges = [ dict(edge.items() | {"length": np.linalg.norm(nodes[edge["node2"]]["point"] - nodes[edge["node1"]]["point"] )}.items())
                     for edge in self.edges]
        self._deleteCross()
        self.sort()
        x = 1

    def sort(self):
        self.edges = sorted(self.edges, key=lambda x: [x["node1"],x["node2"]])

    def _appendPosition(self):
        nodes = self.node.nodes
        pss1  = [nodes[edge["node1"]]["position"] for edge in self.edges]
        pss2  = [nodes[edge["node2"]]["position"] for edge in self.edges]

        self.edges = [dict(edge.items() | {"position" : "in"}.items())
                        for i,edge in enumerate(self.edges )
                     ]
        postype1 = [ps[0] for ps in pss1]
        postype2 = [ps[0] for ps in pss2]
        posno1   = [ps[1:] for ps in pss1]
        posno2   = [ps[1:] for ps in pss2]
        for i,edge in enumerate(self.edges):
            if pss1[i] != "in" and pss2[i] != "in":
                p = nodes[edge["node1"]]["nextnode"]["f"]


    def _deleteCross(self, deleteMode = "min"):
        nodes = self.node.nodes
        ids1 = np.array([self.edges[i]["node1"] for i in range(len(self.edges))])
        ids2 = np.array([self.edges[i]["node2"] for i in range(len(self.edges))])
        nds1 = [nodes[ids1[i]] for i in range(len(ids1))]
        nds2 = [nodes[ids2[i]] for i in range(len(ids2))]
        pts1 = np.array([nds1[i]["point"] for i in range(len(nds1))])
        pts2 = np.array([nds2[i]["point"] for i in range(len(nds2))])
        deleteIndex = []
        continueIndex = []

        
        for i,edge in enumerate(self.edges):
            if nodes[edge["node1"]]["position"] == "in" and nodes[edge["node2"]]["position"] == "in":
                continue
            if nodes[edge["node1"]]["position"] != "in" and nodes[edge["node2"]]["position"] != "in":
                continue
            if i in continueIndex:
                continue

            n1 = nodes[edge["node1"]]
            n2 = nodes[edge["node2"]]
            p1 = n1["point"]
            p2 = n2["point"]

            check1 = self._checkCross(p1, p2, pts1, pts2)
            check2 = (edge["node1"] != ids1)
            check3 = (edge["node2"] != ids1)
            check4 = (edge["node1"] != ids2)
            check5 = (edge["node2"] != ids2)
            check  = check1 & check2 & check3 & check4 & check5
            if np.any(check) == False:
                continue
            crossIndices = np.append(np.where(check)[0], i)
            lengthes = np.array([self.edges[crossIndex]["length"] for crossIndex in crossIndices])
            if deleteMode == "min":
                delIndexTemp = np.amin(lengthes) < lengthes
            elif deleteMode == "max":
                delIndexTemp = np.amax(lengthes) > lengthes
            deleteIndex.extend(list(crossIndices[delIndexTemp]))
            
        deleteIndex = set(deleteIndex)
        self.edges = [self.edges[i] for i in range(len(self.edges)) if i not in deleteIndex]
        print(deleteIndex)


    def _checkCross(self,p1, p2, pts1, pts2):
        b1 = (p2[0] - p1[0]) * (pts1[:,1] - p1[1]) - (p2[1] - p1[1]) * (pts1[:,0] - p1[0])
        b2 = (p2[0] - p1[0]) * (pts2[:,1] - p1[1]) - (p2[1] - p1[1]) * (pts2[:,0] - p1[0])
        b3 = (pts2[:,0] - pts1[:,0]) * (p1[1] - pts1[:,1]) - (pts2[:,1] - pts1[:,1]) * (p1[0] - pts1[:,0])
        b4 = (pts2[:,0] - pts1[:,0]) * (p2[1] - pts1[:,1]) - (pts2[:,1] - pts1[:,1]) * (p2[0] - pts1[:,0])
        return (b1 * b2 < 0) & (b3 * b4 < 0)