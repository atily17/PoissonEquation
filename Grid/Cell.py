import copy

class Cell(object):
    def __init__(self, node, edge):
        self.node = node
        self.edge = edge
        self.cells = []

    def generateCell(self):
        edges = self.edge.edges
        checkEdges = [0 for i in range(len(edges))]
        for i,edge in enumerate(edges):
            if checkEdges[i] == 2:
                continue
            stnode = "node1"
            ednode = "node2"
            n1 = edge[stnode]
            n2 = edge[ednode]
            self.cells.append({"nodes": [n1,n2], "edges":[i]})
            cur_edge = copy.deepcopy(edge)
            nextedge = i
            while(edge["node1"] != n2):
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
                self.cells[-1]["nodes"].append(n2)
                self.cells[-1]["edges"].append(nextedge)

            print(self.cells[-1])
        


class Triangle(Cell):
    def __init__(self, node, edge):
        super().__init__(node, edge)

    def generateCell(self):
        super().generateCell()