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
        bc_node = [node for node in self.nodes if node["position"]!="in"]
        bc_node