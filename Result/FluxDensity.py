import numpy as np
import matplotlib.cm as cm
import matplotlib.pyplot as plt

class FluxDensity(object):
    def __init__(self, grid):
        self.grid = grid

    def calcFluxDensity(self, potentials):
        self.fluxDensity = []

        nodes = [ node for node in self.grid.node.nodes]
        point = [ nodes[i]["point"] for i in range(len(nodes)) ]
        ptntl = [ potentials[i]["potential"] for i in range(len(nodes)) ]

        for i in range(len(nodes)):
            if nodes[i]["position"] != "in":
                continue
            for nextnode in nodes[i]["nextnode"]:
                if nextnode["position"] == "l":
                    l_index = nextnode["no"]
                    dxl = nodes[i]["point"][0] - nodes[l_index]["point"][0]
                elif nextnode["position"] == "r":
                    r_index = nextnode["no"]
                    dxr = nodes[r_index]["point"][0] - nodes[i]["point"][0]
                elif nextnode["position"] == "d":
                    d_index = nextnode["no"]
                    dxd = nodes[i]["point"][1] - nodes[d_index]["point"][1]
                elif nextnode["position"] == "u":
                    u_index = nextnode["no"]
                    dxu = nodes[u_index]["point"][1] - nodes[i]["point"][1]

            ex = -1/(2*(dxl+dxr))*(ptntl[r_index] - ptntl[l_index])
            ey = -1/(2*(dxd+dxu))*(ptntl[u_index] - ptntl[d_index])
            self.fluxDensity.append({"Dx":ex, "Dy":ey, "intensity": np.sqrt(ex**2 + ey**2) , "point":point[i] })

    def plot(self, problem, sizeRate=10):
        size = np.array([problem.domain.right-problem.domain.left, problem.domain.up-problem.domain.down])
        size_normalize=size[0]+size[1]
        size = size/size_normalize * sizeRate

        fig=plt.figure(figsize=size)
        plt.xlim(problem.domain.left,problem.domain.right)
        plt.ylim(problem.domain.down,problem.domain.up)
        ax =fig.add_subplot(1,1,1)
        domain = plt.Polygon(problem.domain.vertexes, zorder=1, fc = "#CCCCFF", ec = "#CCCCFF")

        pointsx = [df["point"][0] for df in self.fluxDensity ]
        pointsy = [df["point"][1] for df in self.fluxDensity ]
        exs     = [df["Dx"] for df in self.fluxDensity ]
        eys     = [df["Dy"] for df in self.fluxDensity ]
        ee      = [np.sqrt(df["intensity"]) for df in self.fluxDensity ]

        cmap = plt.quiver(pointsx, pointsy, exs, eys, ee, alpha=.5, cmap = cm.hsv )
        fig.colorbar(cmap)
        plt.show()

    def print(self):
        print("-----FluxDensity-----")
        for i in range(len(self.fluxDensity)):
            print(self.fluxDensity[i])