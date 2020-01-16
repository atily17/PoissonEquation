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
            if node["position"] != "in":
                self.setMatrixOnBorder(node)
                continue
            nextnodes = list(node["nextnode"].values())
            nextnodes = [self.nodes[nextnode] for nextnode in nextnodes]
            nextnodes = nextnodes + [node]
            diffsi = self.getBasisFunction(node)
            for nextnode in nextnodes:
                j = nextnode["no"]
                nextcells = [self.cells[nodecell] for nodecell in nextnode["cells"] if nodecell in node["cells"]]
                diffsj = self.getBasisFunction(nextnode, nextcells)

                for k in diffsj.keys():
                    diff = diffsi[k]["diff"][0] * diffsj[k]["diff"][0] + diffsi[k]["diff"][1] * diffsj[k]["diff"][1]
                    self.matrix[i,j] -= diff/diffsj[k]["area"]

        return self.matrix

    def getBasisFunction(self, node, cell = None):
        if cell is None:
            cells = [self.cells[nodecell] for nodecell in node["cells"]]
        else:
            cells = cell
        diffs = {}
        for cell in cells:
            cellnodesno = cell["nodes"][:]
            while (cellnodesno[2] != node["no"]):
                f0 = cellnodesno[0]
                cellnodesno.remove(f0)
                cellnodesno.append(f0)
            cellnodes = [self.nodes[cellnode] for cellnode in cellnodesno[:2]]
            area = cell["area"]
            diffx = cellnodes[0]["point"][1] - cellnodes[1]["point"][1]
            diffy = cellnodes[1]["point"][0] - cellnodes[0]["point"][0]
            diffs = {**diffs, cell["no"]: {"area":area,"diff":[diffx, diffy]}}
        return diffs



    def setMatrixOnBorder(self, node):
        i = node["no"]
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

    def setDirichlet(self, node):
        i = node["no"]
        self.matrix[i][i] = 1

    def setNeumann(self, node, t):
        i = node["no"]
        # Vector of Border

        diffsi = self.getBasisFunction(node)

        nextnodes = list(node["nextnode"].values())
        nextnodes = [self.nodes[nextnode] for nextnode in nextnodes]
        nextnodes = nextnodes + [node]

        for nextnode in nextnodes:
            j = nextnode["no"]
            nextcells = [self.cells[nodecell] for nodecell in nextnode["cells"] if nodecell in node["cells"]]
            diffsj = self.getBasisFunction(nextnode, nextcells)

            for k in diffsj.keys():
                diff = diffsi[k]["diff"][0] * diffsj[k]["diff"][0] + diffsi[k]["diff"][1] * diffsj[k]["diff"][1]
                self.matrix[i,j] -= diff/self.cells[k]["area"]

        nextnodes = [self.nodes[nextnode] for k, nextnode in node["nextnode"].items() if self.edges[k]["position"] != "in"]
        bedges = [self.edges[nodeedge] for nodeedge in node["edges"] if self.edges[nodeedge]["position"] != "in"]
        bordercells = [self.cells[bedge["cells"][0]] for bedge in bedges]
