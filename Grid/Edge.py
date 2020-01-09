import numpy as np

class Edge(object):
    def __init__(self, domain, node = None):
        self.domain = domain
        if node is not None:
            self.node = node
        self.edges = []

    def setNo(self):
        self.edges = [ {**self.edges[i] , **{"no": i}} for i in range(len(self.edges))]

    def setEdgeDataNode(self):
        nodes = self.node.nodes
        for node in nodes:
            node["edges"] = []
        for i, edge in enumerate(self.edges):
            nodes[edge["node1"]]["edges"].append(i)
            nodes[edge["node2"]]["edges"].append(i)
        self.__test__setEdgeDataNode()

    def getNextEdges(self, edge_index, node_no = None):
        nodes = self.node.nodes
        if node_no != "node2":
            node1 = self.edges[edge_index]["node1"]
            edges1 = nodes[node1]["edges"][:]
            edges1.remove(edge_index)
        if node_no != "node1":
            node2 = self.edges[edge_index]["node2"]
            edges2 = nodes[node2]["edges"][:]
            edges2.remove(edge_index)
        if node_no == "node1":
            return edges1
        if node_no == "node2":
            return edges2
        return edges1, edges2
    
    def getMinAngleEdge(self, edge_index, a_node = "node2"):
        nodes = self.node.nodes
        if a_node == "node2":
            e_node = "node1"
        elif a_node == "node1":
            e_node = "node2"
        v_node = self.edges[edge_index][a_node]
        point0 = nodes[v_node]["point"]
        point1 = nodes[self.edges[edge_index][e_node]]["point"]
        target_vec = point1 - point0
        nextedges_indeices = self.getNextEdges(edge_index, a_node)
        nextnodes = []
        for nextedges_index in nextedges_indeices:
            if self.edges[nextedges_index]["node1"] == v_node:
                e_node = "node2"
            elif self.edges[nextedges_index]["node2"] == v_node:
                e_node = "node1"
            nextnodes.append(self.edges[nextedges_index][e_node])
        nextpoints = np.array([nodes[nextnode]["point"] for nextnode in nextnodes])
        next_vec = nextpoints - point0
        angle = self.getAngle(target_vec, next_vec)
        max_index = np.argmax(angle)
        return nextedges_indeices[max_index]

    def getAngle(self, vector1, vector2):
        vec1 = vector1 / np.linalg.norm(vector1)
        nn = np.linalg.norm(vector2 , axis = 1)
        vec2 = (vector2.T / np.linalg.norm(vector2 , axis = 1)).T
        cross = vec1[0]*vec2[:,1] - vec1[1]*vec2[:,0]
        dot = vec1[0]*vec2[:,0] + vec1[1]* vec2[:,1]
        dot[cross < 0] += 1
        dot[(cross == 0) & (dot < 0)] = 0
        dot[cross > 0] = dot[cross > 0] * (-1) - 1
        return dot

    def __test__setEdgeDataNode(self):
        nodes = self.node.nodes
        debug = [0 for i in range(len(self.edges))]
        for node in nodes:
            for edge in node["edges"]:
                debug[edge] += 1
        assert(np.all(np.array(debug) == 2))







class Cartesian(Edge):
    def __init__(self, domain ,node=None):
        super().__init__(domain, node)
        if node is not None:
            self.generateEdge()

    def generateEdge(self):
        nodes = self.node.nodes
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
        self.setEdgeDataNode()

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