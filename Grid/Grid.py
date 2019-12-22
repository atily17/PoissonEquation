import matplotlib.pyplot as plt
import numpy as np
from . import Node

class Grid(object):
    def __init__(self, problem, **kwargs):
        self.problem = problem
        self.type = kwargs["type"]
        if self.type=="Cartesian":
            self.node=Node.Cartesian(self.problem.domain, kwargs["div"])
            self.node.putBorder()
            self.node.deleteOverlap()
            self.node.judgeInDomain()
            self.node.sort()
            self.node.setNextNo()

    def plot(self, sizeRate=10):
        size = np.array([self.problem.domain.right-self.problem.domain.left, self.problem.domain.up-self.problem.domain.down])
        size_normalize=size[0]+size[1]
        size = size/size_normalize * sizeRate

        fig=plt.figure(figsize=size)
        plt.xlim(self.problem.domain.left,self.problem.domain.right)
        plt.ylim(self.problem.domain.down,self.problem.domain.up)
        ax =fig.add_subplot(1,1,1)

        co=np.array([[self.node.nodes[i]["point"][0],self.node.nodes[i]["point"][1]] for i in range(len(self.node.nodes))])
        domain = plt.Polygon(self.problem.domain.vertexes, zorder=1, fc = "#DDDDFF")

        ax.add_patch(domain)
        ax.set_axisbelow(True)

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
        plt.scatter(co[:,0],co[:,1] , c="Magenta", zorder=100)
        plt.show()