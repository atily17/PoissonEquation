class Cell(object):
    def __init__(self, node, edge):
        self.node = node
        self.edge = edge

    def generateCell(self):
        edges = self.edge.edges
        node1 = [edge["node1"] for edge in edges ]
        node2 = [edge["node2"] for edge in edges ]


class Triangle(Cell):
    def __init__(self, node, edge):
        super().__init__(node, edge)

    def generateCell(self):
        super().generateCell()