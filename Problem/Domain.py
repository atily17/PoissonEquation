import numpy as np
import copy
import matplotlib.pyplot as plt

class Domain(object):
    def __init__(self, shape, bc):
        self.shape = shape
        self.bc = bc

    def setRange(self, left, right, down, up):
        self.left = left
        self.right = right
        self.down = down
        self.up = up

    def print(self):
        print("-----Domain-----")
        print("#shape")
        print(self.shape)
        print("#Boundary Condition")
        print(self.bc)
        print("#range")
        print(self.left, self.right, self.down, self.up)

class Polygon(Domain):
    def __init__(self, vertexes, bc):
        super().__init__("Polygon", bc)
        self.nVertexes = len(vertexes)
        self.vertexes = np.array(vertexes)

    def calcRange(self):
        l = np.amin(self.vertexes[:,0])
        r = np.amax(self.vertexes[:,0])
        d = np.amin(self.vertexes[:,1])
        u = np.amax(self.vertexes[:,1])
        super().setRange(l,r,d,u)

    def getBorderPoint(self, node, xs, ys, rer=1e-7):
        for i in range(self.nVertexes):
            p1 = self.vertexes[i]
            p2 = self.vertexes[(i + 1) % self.nVertexes]
            if (np.isclose(p1[0], p2[0] , rtol = rer)):
                bordery = np.array([[p1[0], ys[j]] for j in range(len(ys))])
                node_border = [{"point":np.array([bordery[j][0],bordery[j][1]]), "position":"b" + str(i), "nextnode":[] } 
                    for j in range(len(bordery)) if ( (p2[1] - bordery[j][1])*(p1[1] - bordery[j][1]) < 0 )]
                node.extend(copy.deepcopy(node_border[:]))

            elif (np.isclose(p1[1], p2[1] , rtol = rer)):
                borderx = np.array([[xs[j], p1[1]] for j in range(len(xs))])
                node_border = [{"point":np.array([borderx[j][0],borderx[j][1]]), "position":"b" + str(i), "nextnode":[] } 
                    for j in range(len(borderx)) if ( (p2[0] - borderx[j][0])*(p1[0] - borderx[j][0]) < 0 )]
                node.extend(copy.deepcopy(node_border[:]))

            else:
                r = (p2[1] - p1[1]) / (p2[0] - p1[0])
                borderx = np.array([xs, r * (xs - p2[0]) + p2[1]]).T
                borderx = borderx[(p1[0] - borderx[:,0]) * (p2[0] - borderx[:,0]) <= 0]
                node_borderx = [{"point":np.array([borderx[j][0],borderx[j][1]]), "position":"b" + str(i), "nextnode":[] } 
                                for j in range(len(borderx))]
                node.extend(copy.deepcopy(node_borderx[:]))
                r = (p2[0] - p1[0]) / (p2[1] - p1[1])
                bordery = np.array([r * (ys - p2[1]) + p2[0], ys]).T
                bordery = bordery[(p1[1] - bordery[:,1]) * (p2[1] - bordery[:,1]) <= 0]
                node_bordery = [{"point":np.array([bordery[j][0],bordery[j][1]]), "position":"b" + str(i), "nextnode":[] } 
                                for j in range(len(bordery))]
                node.extend(copy.deepcopy(node_bordery[:]))
        return node

    def getCornerPoint(self, node):
        for i in range(self.nVertexes):
            node.append({"point":self.vertexes[i][:], "position":"c" + str(i), "nextnode":[]})

    def getNextNode(self, nodes, rer=1e-7):
        pos0 = np.array([node["position"][0] for node in nodes]) 
        pos1 = np.array([node["position"][1] for node in nodes])
        # on border
        border = pos0 == "b"
        corner = pos0 == "c"
        for i in range(self.nVertexes):
            j = (i + 1) % self.nVertexes
            borderi = (pos1 == str(i)) & border
            corneri = (pos1 == str(i)) & corner
            cornerj = (pos1 == str(j)) & corner

            indexes = np.where(borderi | corneri | cornerj)[0]
            dvertex = self.vertexes[j] - self.vertexes[i]
            pr = 0 if np.abs(dvertex[1]) < rer else 1
            if dvertex[pr] > 0:
                for idx in range(len(indexes)):
                    if idx != 0:
                        nodes[indexes[idx]]["nextnode"].append({"no":indexes[idx-1], "position":"b"})
                    if idx != len(indexes)-1:
                        nodes[indexes[idx]]["nextnode"].append({"no":indexes[idx+1], "position":"f"})
            else:
                for idx in range(len(indexes)):
                    if idx != 0:
                        nodes[indexes[idx]]["nextnode"].append({"no":indexes[idx-1], "position":"f"})
                    if idx != len(indexes)-1:
                        nodes[indexes[idx]]["nextnode"].append({"no":indexes[idx+1], "position":"b"})


    def deleteOutDomain(self, node, thetaerr=6):
        pts = np.array([node[i]["point"] for i in range(len(node))])
        pos = np.array([node[i]["position"] for i in range(len(node))])
        theta = np.zeros(len(pts))
        thetas = 0
        for i in range(self.nVertexes):
            p1 = self.vertexes[i]
            p2 = self.vertexes[(i + 1) % self.nVertexes]
            v1 = (pts - p1)
            v2 = (pts - p2)
            dot = v1[:,0] * v2[:,0] + v1[:,1] * v2[:,1]
            cross = v1[:,0] * v2[:,1] - v1[:,1] * v2[:,0]
            vn1 = np.linalg.norm(v1, axis=1)
            vn2 = np.linalg.norm(v2, axis=1)
            theta = np.arccos(np.clip(dot / (vn1 * vn2), -1, 1))
            thetas += np.sign(cross)*np.array(theta)
        inx = np.where( ((pos == "nd") & ~(thetas < thetaerr)))[0]
      
        for i in inx:
            node[i]["position"]="in"

    def print(self):
        super().print()
        print("n_vertexes", self.nVertexes)
        print("vertexes", self.vertexes)

    def plot(self, sizeRate=10):
        size = np.array([self.right - self.left, self.up - self.down])
        size_normalize = size[0] + size[1]
        size = size / size_normalize * sizeRate

        fig = plt.figure(figsize=size)
        plt.xlim(self.left, self.right)
        plt.ylim(self.down, self.up)
        ax = fig.add_subplot(1,1,1)
        domain = plt.Polygon(self.vertexes, zorder=1, fc = "#DDDDFF")

        ax.add_patch(domain)
        ax.set_axisbelow(True)

        zz = 10 + self.nVertexes
        for k in self.bc["priority"]:
            e1 = k
            e2 = (k + 1) % self.nVertexes

            if self.bc["bc"][k]["bctype"] == "Dirichlet":
                c = "b-"
            elif self.bc["bc"][k]["bctype"] == "Neumann":
                c = "r-"

            plt.plot([self.vertexes[e1][0],self.vertexes[e2][0]], [self.vertexes[e1][1],self.vertexes[e2][1]], c, zorder = zz, lw=5)
            zz -= 1

        plt.show()