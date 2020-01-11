import matplotlib.pyplot as plt
import matplotlib.collections as mcl
import numpy as np
from . import Node
from . import Edge
from . import Cell

class Grid(object):
    def __init__(self, problem, node = None, type = None):
        self.problem = problem
        if type == "FDM":
            self._setNodeCaseFDM(**node["node"])
        elif type == "FEM":
            self._setNodeCaseFEM(**node)


    def setNode(self, **node):
        self.nodeType = node["type"]
        if self.nodeType =="Cartesian":
            if "eps" in node:
                self.node=Node.Cartesian(self.problem.domain, node["div"], node["eps"])
            else :
                self.node=Node.Cartesian(self.problem.domain, node["div"])
            self.node.putBorder()
            self.node.deleteOverlap()
            self.node.judgeInDomain()
            self.node.sort()
            self.node.setNextNo()

    def setEdge(self, **edge):
        self.edgeType = edge["type"]
        if self.edgeType == "Cartesian":
            assert self.nodeType == "Cartesian", "if edge type is 'Cartesian', grid['type'] must be 'Cartesian'"
            self.edge = Edge.Cartesian(self.node)

    def setCell(self, **cell):
        self.cellType = cell["type"]
        if self.cellType == "Cartesian":
            assert self.nodeType == "Cartesian", "if edge type is 'Cartesian', grid['type'] must be 'Cartesian'"
            self.cell = Cell.Cartesian(self.node, self.edge)

    def _setNodeCaseFDM(self, **node):
        self.nodeType = node["type"]
        if self.nodeType =="Cartesian":
            if "eps" in node:
                self.node=Node.Cartesian(self.problem.domain, node["div"], node["eps"])
            else :
                self.node=Node.Cartesian(self.problem.domain, node["div"])
            self.node.putBorder()
            self.node.deleteOverlap()
            self.node.judgeInDomain()
            self.node.sort()
            self.node.setNextNo()

    def _setNodeCaseFEM(self, **grid):
        node = grid["node"]
        edge = grid["edge"]
        cell = grid["cell"]
        self.nodeType = node["type"]
        self.edgeType = edge["type"]
        if self.nodeType =="Cartesian":
            if "eps" in node:
                self.node=Node.Cartesian(self.problem.domain, node["div"], node["eps"])
            else :
                self.node=Node.Cartesian(self.problem.domain, node["div"], 3)
            self.node.putBorder()
            self.node.deleteOverlap("eps")
            self.node.judgeInDomain()
            self.node.sort()
            self.node.setNextNo()
            self.node.setNo()

        if self.edgeType == "NotCross":
            self.edge = Edge.Cartesian(self.problem.domain, self.node)
            self.edge.setNo()
        
        self.cell = Cell.Triangle(self.node, self.edge)
        self.edge.cell = self.cell
        self.cell.generateCell()
        self.cell.splitTriangle()
        self.cell.flipTriangle()
        self.cell.getNo()
        self.cell.getArea()

        self.edge.print()
        self.cell.print()

    def print(self, gridType = "all"):
        print("-----Grid-----")
        if gridType == "all" or gridType == "Node":
            self.node.print()

    def plot(self, sizeRate=10):
        size = np.array([self.problem.domain.right-self.problem.domain.left, self.problem.domain.up-self.problem.domain.down])
        size_normalize=size[0]+size[1]
        size = size/size_normalize * sizeRate

        fig=plt.figure(figsize=size)
        plt.xlim(self.problem.domain.left,self.problem.domain.right)
        plt.ylim(self.problem.domain.down,self.problem.domain.up)
        ax =fig.add_subplot(1,1,1)
        
        # Domain
        domain = plt.Polygon(self.problem.domain.vertexes, zorder=1, fc = "#DDDDFF")
        ax.add_patch(domain)
        zz = 10+self.problem.domain.nVertexes
        for k in self.problem.domain.bc["priority"]:
            e1 = k
            e2 = (k + 1) % self.problem.domain.nVertexes

            if self.problem.domain.bc["bc"][k]["bctype"] == "Dirichlet":
                c = "b-"
            elif self.problem.domain.bc["bc"][k]["bctype"] == "Neumann":
                c = "r-"

            print(e1, e2)
            plt.plot([self.problem.domain.vertexes[e1][0],self.problem.domain.vertexes[e2][0]],
                     [self.problem.domain.vertexes[e1][1],self.problem.domain.vertexes[e2][1]],
                     c, zorder = zz, lw=5)
            zz -= 1
        # Node
        co=np.array([[self.node.nodes[i]["point"][0],self.node.nodes[i]["point"][1]] for i in range(len(self.node.nodes))])
        plt.scatter(co[:,0],co[:,1] , c="Magenta", zorder=100)

        # Edge
        try:
            edges = self.edge.edges
            egs=mcl.LineCollection([[self.node.nodes[edge["node1"]]["point"],self.node.nodes[edge["node2"]]["point"]] for edge in edges])
            ax.add_collection(egs) #, colors="k", zorder=100)
        except:
            1

        plt.show()

