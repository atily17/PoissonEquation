import numpy as np

class VectorGenerater(object):
    def generate(self, problem, grid):
        self.nodes = grid.node.nodes
        self.edges = grid.edge.edges
        nodes = grid.node.nodes
        self.vector = np.zeros(len(nodes))
        for i in range(len(nodes)):
            if nodes[i]["position"][0] == "i":
                self.vector[i] = problem.source.source(nodes[i]["point"])
            elif "b" in nodes[i]["position"][0]:
                if problem.domain.bc["bc"][int(nodes[i]["position"][1:])]["bctype"] == "Neumann":
                    bc = problem.domain.bc["bc"][int(nodes[i]["position"][1:])]
                    self.setNeumann(nodes[i], bc)
                if problem.domain.bc["bc"][int(nodes[i]["position"][1:])]["bctype"] == "Dirichlet":
                    self.vector[i] = problem.domain.bc["bc"][int(nodes[i]["position"][1:])]["constant"]
            elif "c" in nodes[i]["position"][0]:
                if problem.domain.bc["priority"] is None:
                    self.vector[i] = problem.domain.bc[int(grid.lattice.nodes[i].position[1:])][1]
                    self.vector[i] = problem.domain.bc[int(grid.lattice.nodes[i].position[1:]) - 1][1]
                    self.vector[i]/=2
                elif type(problem.domain.bc["priority"]) == list:
                    k1 = int(nodes[i]["position"][1:])
                    k2 = (int(nodes[i]["position"][1:]) - 1) % problem.domain.nVertexes
                    index1 = problem.domain.bc["priority"].index(k1)
                    index2 = problem.domain.bc["priority"].index(k2)
                    if index1 < index2:
                        self.vector[i] = problem.domain.bc["bc"][k1]["constant"]
                    if index1 > index2:
                        self.vector[i] = problem.domain.bc["bc"][k2]["constant"]
        return self.vector

    def getBorderBasisFunction(self, node, edge=None):
        if edge is None:
            edges = [self.edges[nodeedge] for nodeedge in node["edges"] if self.edges[nodeedge]["position"] != "in"]
        else:
            edges = edge
        bfunc = {}
        for edge in edges:
            cell = edge["cells"][0]
            bfunc = {**bfunc, cell: {"length":[edge["length"] / 2, edge["length"] / 2], "position": int(edge["position"][1:])}}
        return bfunc

    def setNeumann(self, node, bc):
        edges = [self.edges[nodeedge] for nodeedge in node["edges"] if self.edges[nodeedge]["position"] != "in"]
        for edge in edges:
            self.vector[node["no"]] += edge["length"] * bc["constant"]