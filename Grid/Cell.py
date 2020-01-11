import copy
import numpy as np

class Cell(object):
    def __init__(self, node, edge):
        self.node = node
        self.edge = edge
        self.cells = []
        self.eps = self.node.eps[0]**2 * self.node.eps[1]**2

    def generateCell(self):
        self.cells = []
        edges = self.edge.edges
        checkEdges = [{"node1":False, "node2":False} for i in range(len(edges))]
        for i,edge in enumerate(edges):
            for stnode in ["node1", "node2"]:
                bsnode = stnode
                if checkEdges[i][stnode]:
                    continue
                if stnode == "node1":
                    ednode = "node2"
                elif stnode == "node2":
                    ednode = "node1"
                n1 = edge[stnode]
                n2 = edge[ednode]
                self.cells.append({"nodes": [n1], "edges":[i]})
                checkEdges[i][stnode] = True
                cur_edge = copy.deepcopy(edge)
                nextedge = i
                while(edge[bsnode] != n2):
                    n1 = n2
                    nextedge = self.edge.getMinAngleEdge(nextedge, ednode)
                    cur_edge = copy.deepcopy(edges[nextedge])
                    if cur_edge["node1"] == n1:
                        stnode = "node1"
                        ednode = "node2"
                    elif cur_edge["node2"] == n1:
                        stnode = "node2"
                        ednode = "node1"
                    n2 = cur_edge[ednode]
                    self.cells[-1]["nodes"].append(n1)
                    self.cells[-1]["edges"].append(nextedge)
                    checkEdges[nextedge][stnode] = True

        # check outer cell
        edgesposition = [ np.array([edges[cellEdge]["position"] for cellEdge in cell["edges"]]) for cell in self.cells]
        self.cells = [cell for i, cell in enumerate(self.cells) if np.any(edgesposition[i] == "in") ]

        # get the number of edges
        self.cells = [{**cell, "n_vertexes": len(cell["nodes"])} for cell in self.cells]
        self._test_checkCellExistArea()

    def getNo(self):
        self.cells = [ {**self.cells[i] , "no": i} for i in range(len(self.cells))]

    def splitCell(self, cellNo, diagonalNo1, diagonalNo2):
        cell = self.cells[cellNo]
        n_vertexes = cell["n_vertexes"]
        n = (diagonalNo1 - diagonalNo2) % n_vertexes
        if n == 1 or n == n_vertexes - 1 or n == 0:
            return False

        nodes = self.node.nodes

        nodeNo1 = self.cells[cellNo]["nodes"][diagonalNo1]
        nodeNo2 = self.cells[cellNo]["nodes"][diagonalNo2]
        node1point = nodes[nodeNo1]["point"]
        node2point = nodes[nodeNo2]["point"]

        cellnodes = [nodes[cell["nodes"][i]] for i in range(len(cell["nodes"]))]
        cellnodespoints = np.array([cellnode["point"] for cellnode in cellnodes])
        vec1 = node2point - node1point
        vecs2 = cellnodespoints - node1point
        bools = np.array([False for i in range(len(vecs2))])
        r = ( vec1[0] * vecs2[:,0] + vec1[1] * vecs2[:,1]) / ( vec1[0] * vec1[0] + vec1[1] * vec1[1])
        bools[(r < (self.eps) ) | ((1 - self.eps) < r)] = True
        areas = np.abs(vec1[0] * vecs2[:,1] - vec1[1] * vecs2[:,0])
        bools[areas > self.eps] = True
        if ~np.all(bools):
            return False
        
        edges = self.edge.edges
        tempedge = {"node1":nodeNo1, "node2":nodeNo2, "no":len(edges), "position":"in"}
        self.edge.setEdgeLength(tempedge)
        edges.append(tempedge)
        self.edge.setEdgeDataNode(edges[-1])
        if diagonalNo1 < diagonalNo2:
            l_diagonalNo = diagonalNo1
            g_diagonalNo = diagonalNo2
        else:
            l_diagonalNo = diagonalNo2
            g_diagonalNo = diagonalNo1
        cell1nodes = cell["nodes"][l_diagonalNo : g_diagonalNo+1]
        cell1edges = cell["edges"][l_diagonalNo : g_diagonalNo] + [edges[-1]["no"]]
        cell1vertex = len(cell1nodes)
        cell1 = {"nodes": cell1nodes, "edges": cell1edges, "n_vertexes": cell1vertex}
        
        cell2nodes = cell["nodes"][g_diagonalNo :] + cell["nodes"][: l_diagonalNo + 1]
        cell2edges = cell["edges"][g_diagonalNo :] + cell["edges"][: l_diagonalNo] + [edges[-1]["no"]]
        cell2vertex = len(cell2nodes)
        cell2 = {"nodes": cell2nodes, "edges": cell2edges, "n_vertexes": cell2vertex}
        
        self.cells[cellNo] = cell1
        self.cells.append(cell2)
        return True

    def _test_checkCellExistArea(self):
        for cell in self.cells:
            assert(cell["n_vertexes"] > 2 )

    def print(self):
        for i in range(len(self.cells)):
            print(i, self.cells[i])

class Triangle(Cell):
    def __init__(self, node, edge):
        super().__init__(node, edge)

    def generateCell(self):
        super().generateCell()

    def splitTriangle(self):
        edges = self.edge.edges
        for i,cell in enumerate(self.cells):
            n1 = 0
            n2 = 2
            while(self.cells[i]["n_vertexes"] != 3):
                if (self.splitCell(i,n1,n2)):
                    n1 = 0
                    n2 = 2
                    continue
                n2 += 1
                if (n2 == cell["n_vertexes"]):
                    n1 += 1
                    n2 = n1 + 2
                    assert(n2 < self.cells[i]["n_vertexes"])

        self.edge.setAllEdgeAdjacentCell()
        self.print()
        #self.generateCell()

    def flipTriangle(self):
        nodes = self.node.nodes
        edges = self.edge.edges
        for edge in edges:
            if edge["position"] != "in":
                continue
            # check whether flipping
            cell1 = self.cells[edge["cells"][0]]
            cell2 = self.cells[edge["cells"][1]]
            tempnodes = set(copy.deepcopy(cell1["nodes"]) + copy.deepcopy(cell2["nodes"]))
            tempnodes.remove(edge["node1"])
            tempnodes.remove(edge["node2"])
            tempnodes = list(tempnodes)

            nodepoint = nodes[edge["node1"]]["point"]
            temppoint = np.array([ nodes[tempnodes[i]]["point"] for i in range(len(tempnodes)) ])

            circumcenter = self.getCircumcenter(cell1)
            radvec = nodepoint - circumcenter
            tempvec = temppoint - circumcenter

            radius   = radvec[0]**2 + radvec[1]**2
            distance = tempvec[:,0]**2 + tempvec[:,1]**2
            if np.any(distance + self.eps < radius):
                self._flip(edge)

    def _flip(self, edge):
        print(edge["no"], "Flipping!")
        # TODO: setting cell
        # 四角形を作ってからが良さそう
        rect = self.getRectangle(edge)
        print(rect)
        cell1 = self.cells[edge["cells"][0]]
        cell2 = self.cells[edge["cells"][1]]

        edge["node1"] = rect["nodes"][1]
        edge["node2"] = rect["nodes"][3]

        cell1["nodes"] = [rect["nodes"][0],rect["nodes"][1],rect["nodes"][3]]
        cell2["nodes"] = [rect["nodes"][2],rect["nodes"][3],rect["nodes"][1]]
        cell1["edges"] = [rect["edges"][0],edge["no"], rect["edges"][3]]
        cell2["edges"] = [rect["edges"][1],edge["no"], rect["edges"][2]]


    def getRectangle(self, edge):
        cell1 = copy.deepcopy(self.cells[edge["cells"][0]])
        cell2 = copy.deepcopy(self.cells[edge["cells"][1]])

        nodes1 = cell1["nodes"][:]
        edges1 = cell1["edges"][:]
        nodes2 = cell2["nodes"][:]
        edges2 = cell2["edges"][:]

        while(edges1.index(edge["no"]) !=2 ):
            f0 = edges1[0]
            edges1.remove(f0)
            edges1.append(f0)
            f0 = nodes1[0]
            nodes1.remove(f0)
            nodes1.append(f0)
        while(edges2.index(edge["no"]) !=2 ):
            f0 = edges2[0]
            edges2.remove(f0)
            edges2.append(f0)
            f0 = nodes2[0]
            nodes2.remove(f0)
            nodes2.append(f0)

        rectedges = edges1[:len(edges1)-1] + edges2[:len(edges2)-1]
        rectnodes = nodes1[:len(nodes1)-1] + nodes2[:len(nodes2)-1]
        rect = {"nodes":rectnodes, "edges":rectedges}
        return rect

    def getCircumcenter(self, cell):
        if type(cell) == int:
            cell = self.cells[cell]
        nodes = self.node.nodes
        nodesNo = cell["nodes"]
        nodesPt = [nodes[nodeNo]["point"] for nodeNo in nodesNo ]

        dots = []
        for i in range(3):
            j = (i+1)%3
            k = (j+1)%3
            dots.append(np.dot(nodesPt[j] - nodesPt[k], nodesPt[j] - nodesPt[k]))

        pp = []
        for i in range(3):
            j = (i+1)%3
            k = (j+1)%3
            pp.append(dots[i] * (dots[j] + dots[k] - dots[i]))

        circumcenter = (pp[0]*nodesPt[0] + pp[1]*nodesPt[1] + pp[2]*nodesPt[2])/(pp[0] + pp[1] + pp[2])
        return circumcenter

    def getArea(self, cell = None):
        if cell is None :
            self.getAllArea()

    def getAllArea(self):
        nodes = self.node.nodes
        cellsnodes = [cell["nodes"][:] for cell in self.cells]
        cellsnodespoint = np.array([[nodes[cellnode]["point"] for cellnode in cellnodes] for cellnodes in cellsnodes])

        vec1 = cellsnodespoint[:,1,:] - cellsnodespoint[:,0,:]
        vec2 = cellsnodespoint[:,2,:] - cellsnodespoint[:,0,:]

        areas = np.abs(vec1[:,0]*vec2[:,1] - vec2[:,0]*vec1[:,1])/2
        self.cells = [{**self.cells[i], "area":areas[i]} for i in range(len(self.cells))]