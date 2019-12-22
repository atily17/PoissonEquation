import numpy as np

class VectorGenerater(object):
    def generate(self, problem, grid):
        nodes = grid.node.nodes
        vector = np.zeros(len(nodes))
        for i in range(len(nodes)):
            if nodes[i]["position"][0] == "i":
                vector[i] = problem.source.source(nodes[i]["point"])
            elif "b" in nodes[i]["position"][0]:
                vector[i] = problem.domain.bc["bc"][int(nodes[i]["position"][1:])]["constant"]
            elif "c" in nodes[i]["position"][0]:
                if problem.domain.bc["priority"] is None:
                    vector[i]=problem.domain.bc[int(grid.lattice.nodes[i].position[1:])][1]
                    vector[i]=problem.domain.bc[int(grid.lattice.nodes[i].position[1:]) - 1][1]
                    vector[i]/=2
                elif type(problem.domain.bc["priority"]) == list:
                    k1 =  int(nodes[i]["position"][1:])
                    k2 = (int(nodes[i]["position"][1:]) - 1) % problem.domain.nVertexes
                    index1 = problem.domain.bc["priority"].index(k1)
                    index2 = problem.domain.bc["priority"].index(k2)
                    if index1 < index2:
                        vector[i]=problem.domain.bc["bc"][k1]["constant"]
                    if index1 > index2:
                        vector[i]=problem.domain.bc["bc"][k2]["constant"]
        return vector