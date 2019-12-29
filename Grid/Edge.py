import numpy as np

class Edge(object):
    def __init__(self):
        pass

class Cartesian(Edge):
    def __init__(self, node = None):
        if node is not None:
            self.nodes = node.nodes
            self.generateEdge()

    def generateEdge(self):
        self.edges = []
        self.edges.extend([{"p1":i, "p2": self.nodes[i]["nextnode"]["f"]} for i in range(len(self.nodes)) if "f" in self.nodes[i]["nextnode"]])
        self.edges.extend([{"p1":i, "p2": self.nodes[i]["nextnode"]["r"]} for i in range(len(self.nodes)) if "r" in self.nodes[i]["nextnode"]])
        self.edges.extend([{"p1":i, "p2": self.nodes[i]["nextnode"]["u"]} for i in range(len(self.nodes)) if "u" in self.nodes[i]["nextnode"]])
        x=1