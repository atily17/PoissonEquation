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
                node_border = [{"point":np.array([bordery[j][0],bordery[j][1]]), "position":"b" + str(i), "nextnode":{} } 
                    for j in range(len(bordery)) if ((p2[1] - bordery[j][1]) * (p1[1] - bordery[j][1]) < 0)]
                node.extend(copy.deepcopy(node_border[:]))

            elif (np.isclose(p1[1], p2[1] , rtol = rer)):
                borderx = np.array([[xs[j], p1[1]] for j in range(len(xs))])
                node_border = [{"point":np.array([borderx[j][0],borderx[j][1]]), "position":"b" + str(i), "nextnode":{} } 
                    for j in range(len(borderx)) if ((p2[0] - borderx[j][0]) * (p1[0] - borderx[j][0]) < 0)]
                node.extend(copy.deepcopy(node_border[:]))

            else:
                r = (p2[1] - p1[1]) / (p2[0] - p1[0])
                borderx = np.array([xs, r * (xs - p2[0]) + p2[1]]).T
                borderx = borderx[(p1[0] - borderx[:,0]) * (p2[0] - borderx[:,0]) <= 0]
                node_borderx = [{"point":np.array([borderx[j][0],borderx[j][1]]), "position":"b" + str(i), "nextnode":{} } 
                                for j in range(len(borderx))]
                node.extend(copy.deepcopy(node_borderx[:]))
                r = (p2[0] - p1[0]) / (p2[1] - p1[1])
                bordery = np.array([r * (ys - p2[1]) + p2[0], ys]).T
                bordery = bordery[(p1[1] - bordery[:,1]) * (p2[1] - bordery[:,1]) <= 0]
                node_bordery = [{"point":np.array([bordery[j][0],bordery[j][1]]), "position":"b" + str(i), "nextnode":{} } 
                                for j in range(len(bordery))]
                node.extend(copy.deepcopy(node_bordery[:]))
        return node

    def getCornerPoint(self, node):
        for i in range(self.nVertexes):
            node.append({"point":self.vertexes[i][:], "position":"c" + str(i), "nextnode":{}})

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
                        nodes[indexes[idx]]["nextnode"].setdefault("b", indexes[idx - 1])
                    if idx != len(indexes) - 1:
                        nodes[indexes[idx]]["nextnode"].setdefault("f", indexes[idx + 1])
            else:
                for idx in range(len(indexes)):
                    if idx != 0:
                        nodes[indexes[idx]]["nextnode"]["f"] = indexes[idx - 1]
                    if idx != len(indexes) - 1:
                        nodes[indexes[idx]]["nextnode"]["b"] = indexes[idx + 1]


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
            thetas += np.sign(cross) * np.array(theta)
        inx = np.where(((pos == "nd") & ~(thetas < thetaerr)))[0]
      
        for i in inx:
            node[i]["position"] = "in"

    def isNextNodeNearBorder(self, node0, node1, ebs):
        pos0 = node0["position"]
        pos1 = node1["position"]
        if pos0 == pos1:
            return False
        if np.linalg.norm(node0["point"]- node1["point"]) > np.linalg.norm(ebs):
            return False
        postype0 = node0["position"][0]
        postype1 = node1["position"][0]
        posnum0 = int(node0["position"][1:])
        posnum1 = int(node1["position"][1:])
        if ((postype0 == "c") and (postype1 == "c") and ((posnum1 - posnum0) % self.nVertexes == 1 or ((posnum1 - posnum0) % self.nVertexes == self.nVertexes - 1))):
            return False
        if ((postype0 == "b") and (postype1 == "c") and ((posnum0 == posnum1) or (posnum0 == (posnum1 - 1) % self.nVertexes))):
            return False
        if ((postype0 == "c") and (postype1 == "b") and ((posnum0 == posnum1) or (posnum0 == (posnum1 + 1) % self.nVertexes))):
            return False

        pm = (node0["point"] + node1["point"]) / 2
        if postype0 == "b":
            vp0 = self.vertexes[posnum0]
            vp1 = self.vertexes[(posnum0 + 1) % self.nVertexes]
            vVec = vp1 - vp0
            pVec = pm - vp0
            b0 = (vVec[0] * pVec[1] - vVec[1] * pVec[0]) > 0
        else:
            vp0 = self.vertexes[posnum0]
            vp1 = self.vertexes[(posnum0 + 1) % self.nVertexes]
            vp2 = self.vertexes[(posnum0 - 1) % self.nVertexes]
            vVec1 = vp1 - vp0
            vVec2 = vp0 - vp2
            pVec1 = pm - vp0
            pVec2 = pm - vp2
            b0 = (vVec1[0] * pVec1[1] - vVec1[1] * pVec1[0]) > 0
            b0 &= (vVec2[0] * pVec2[1] - vVec2[1] * pVec2[0]) > 0

        if postype1 == "b":
            vp0 = self.vertexes[posnum1]
            vp1 = self.vertexes[(posnum1 + 1) % self.nVertexes]
            vVec = vp1 - vp0
            pVec = pm - vp0
            b1 = (vVec[0] * pVec[1] - vVec[1] * pVec[0]) > 0
        else:
            vp0 = self.vertexes[posnum1]
            vp1 = self.vertexes[(posnum1 + 1) % self.nVertexes]
            vp2 = self.vertexes[(posnum1 - 1) % self.nVertexes]
            vVec1 = vp1 - vp0
            vVec2 = vp0 - vp2
            pVec1 = pm - vp0
            pVec2 = pm - vp2
            b1 = (vVec1[0] * pVec1[1] - vVec1[1] * pVec1[0]) > 0
            b1 &= (vVec2[0] * pVec2[1] - vVec2[1] * pVec2[0]) > 0

        return b0 & b1

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