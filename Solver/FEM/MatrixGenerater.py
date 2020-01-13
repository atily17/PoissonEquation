import numpy as np
import copy

class MatrixGenerater(object):
    def generate(self, problem, grid, case="2nd"):
        self.eps = grid.node.eps
        self.nodes = grid.node.nodes
        self.edges = grid.edge.edges
        self.cells = grid.cell.cells
        self.bc = problem.domain.bc
        self.domain = problem.domain
        return self._case2ndAcuracy()

    def _case2ndAcuracy(self):
        self.matrix = np.zeros((len(self.nodes), len(self.nodes)))
        for i, node in enumerate(self.nodes):
            if node["position"][0] != "in":
                self.setMatrixOnBorder(node)
            nextnodes = list(node["nextnode"].values())
            nextnodes = [self.nodes[nextnode] for nextnode in nextnodes]
            nextnodes = nextnodes + [node]
            diffsi = self.getBasisFunction(node)
            print(diffsi)
            for nextnode in nextnodes:
                j = nextnode["no"]
                nextcells = [self.cells[nodecell] for nodecell in nextnode["cells"] if nodecell in node["cells"]]
                diffsj = self.getBasisFunction(nextnode, nextcells)
                print(diffsj)

                for k in diffsj.keys():
                    diff = diffsi[k]["x"] * diffsj[k]["x"] + diffsi[k]["y"] * diffsi[k]["y"] * diffsj[k]["y"]
                    self.matrix[i,j] += diff

        print(self.matrix)


    def getBasisFunction(self, node, cell = None):
        if cell is None:
            cells = [self.cells[nodecell] for nodecell in node["cells"]]
        else:
            cells = cell
        diffs = {}
        for cell in cells:
            cellnodes = [self.nodes[cellnode] for cellnode in cell["nodes"] if cellnode != node["no"]]
            area = cell["area"]
            diffx = cellnodes[0]["point"][1] - cellnodes[1]["point"][1]
            diffy = cellnodes[1]["point"][0] - cellnodes[0]["point"][0]
            diffs = {**diffs, cell["no"]: {"x":diffx/area, "y":diffy/area}}

        return diffs

    def setMatrixOnBorder(self, node):
        i = node["i"]
        assert (node["position"][0] == "b" or node["position"][0] == "c"), node["position"]
        if node["position"][0] == "b":
            t = int(node["position"][1])
            bctype = self.bc["bc"][t]["bctype"]
        elif node["position"][0] == "c":
            t = int(node["position"][1])
            l = len(self.bc["bc"])
            b1 = (t - 1) % l
            b2 = t
            c1 = self.bc["priority"].index(b1)
            c2 = self.bc["priority"].index(b2)
            assert c1 != c2, "priority is odd"
            if c1 < c2:
                t = b1
                bctype = self.bc["bc"][b1]["bctype"]
            elif c2 < c1:
                t = b2
                bctype = self.bc["bc"][b2]["bctype"]
        if bctype == "Neumann":
            self.setNeumann(node, t)
        elif bctype == "Dirichlet":
            self.setDirichlet(node)

    def setDirichlet(node):
        i = node["no"]
        self.matrix[i][i] = 1

    def setNeumann(node, t):
        i = node["no"]
        #TODO: