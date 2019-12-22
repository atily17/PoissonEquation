import numpy as np
import matplotlib.cm as cm
import matplotlib.pyplot as plt

class Potential(object):
    def __init__(self, potentials, grid):
        nodes = grid.node.nodes
        self.potentials = [{ "potential":potentials[i], "point":nodes[i]["point"]} for i in range(len(nodes))]

    def print(self):
        for i in range(len(self.potentials)):
            print(self.potentials[i])

    def plot(self, problem, plottype = "normal", sizeRate=10, zeroOrder=-35):
        size = np.array([problem.domain.right-problem.domain.left, problem.domain.up-problem.domain.down])
        size_normalize=size[0]+size[1]
        size = size/size_normalize * sizeRate

        fig=plt.figure(figsize=size)
        plt.xlim(problem.domain.left,problem.domain.right)
        plt.ylim(problem.domain.down,problem.domain.up)
        ax =fig.add_subplot(1,1,1)
        domain = plt.Polygon(problem.domain.vertexes, zorder=1, fc = "#CCCCFF", ec = "#CCCCFF")

        ax.add_patch(domain)
        ax.set_axisbelow(True)

        co  = np.array([[self.potentials[i]["point"][0],self.potentials[i]["point"][1]] for i in range(len(self.potentials))])
        val = np.array([self.potentials[i]["potential"] for i in range(len(self.potentials))])
       
        
        pl  =co[val>10**(zeroOrder)];
        c0  =co[(val<10**(zeroOrder)) & (val>-10**(zeroOrder))]
        mi  =co[val<-10**(zeroOrder)];
        
        if (plottype == "normal"):
            cmap = plt.scatter(co[:,0],co[:,1] , c=val , cmap=cm.hsv, zorder=2, marker='.')

        elif (plottype == "log"):
            plt.scatter(pl[:,0],pl[:,1] , c=np.log10(val[val>10**(zeroOrder)]) , cmap=cm.Reds, zorder=2, marker='.')
            plt.scatter(c0[:,0],c0[:,1] , c="#FFFFFF", zorder=2, marker='.')
            plt.scatter(mi[:,0],mi[:,1] , c=np.log10(-val[val<-10**(zeroOrder)]), cmap=cm.Blues, zorder=2, marker='.')
        fig.colorbar(cmap)
        plt.show()