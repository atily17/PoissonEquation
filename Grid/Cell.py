import copy
import numpy as np

class Cell(object):
    def __init__(self, node, edge):
        self.node = node
        self.edge = edge
        self.cells = []

    def generateCell(self):
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

    def _test_checkCellExistArea(self):
        for cell in self.cells:
            assert(cell["n_vertexes"] > 2 )

class Triangle(Cell):
    def __init__(self, node, edge):
        super().__init__(node, edge)

    def generateCell(self):
        super().generateCell()

    def splitTriangle(self):
        for cell in self.cells:
            if cell["n_vertexes"] == 3:
                continue
            cell["node"]