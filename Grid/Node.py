import matplotlib.pyplot as plt
import numpy as np
import itertools
from . import Node

class Node(object):
    def __init__(self):
        pass

    def judgeInOut(self, domain, point):
        pass


class Cartesian(Node):
    def __init__(self, domain, div, epsilon = 4):
        self.domain = domain
        if isinstance(div[0], (int)):
            self.nDivX = div[0]
            self.xs = np.linspace(self.domain.left, self.domain.right, self.nDivX)
        else:
            self.nDivX = len(div[0])
            self.xs = np.array(div[0])
            self.xs = np.sort(self.xs)
            d = (self.domain.right - self.domain.left) / (self.xs[-1] - self.xs[0])
            self.xs = d * self.xs
        if isinstance(div[1], (int)):
            self.nDivY = div[1]
            self.ys = np.linspace(self.domain.down, self.domain.up   , self.nDivY)
        else:
            self.nDivY = len(div[1])
            self.ys = div[1]
            self.ys = np.sort(self.ys)
            d = (self.domain.up - self.domain.down) / (self.ys[-1] - self.ys[0])
            self.ys = d * self.ys
        self.nodes = [{"point":np.array([self.xs[i],self.ys[j]]), "position":"nd", "nextnode":[] } 
                    for i,j in itertools.product(range(self.nDivX), range(self.nDivY))]
        epsx = (self.domain.right - self.domain.left)/self.nDivX/epsilon
        epsy = (self.domain.up - self.domain.down)/self.nDivY/epsilon
        self.eps  = np.array([epsx,epsy])

    def putBorder(self):
        self.domain.getBorderPoint(self.nodes, self.xs, self.ys)
        self.domain.getCornerPoint(self.nodes)

    def deleteOverlap(self):
        # Delete overlap nodes on vertexes
        pos = np.array([self.nodes[i]["position"][0] for i in range(len(self.nodes))] , dtype=str)
        pts = np.array([self.nodes[i]["point"] for i in range(len(self.nodes))])
        deleteindex = []
        indexes = np.where(pos[:] == "c")[0]
        for ix in indexes:
            pb = np.where((np.abs(pts[:,0] - pts[ix,0]) < self.eps[0] ) & (np.abs(pts[:,1] - pts[ix,1]) < self.eps[1] ) & (pos[:] != "c"))[0]
            deleteindex.extend(pb)
        self.nodes = [self.nodes[i] for i in range(len(self.nodes)) if i not in deleteindex]

        # Delete overlap nodes on Borders
        pos = np.array([self.nodes[i]["position"][0] for i in range(len(self.nodes))] , dtype=str)
        posf = np.array([self.nodes[i]["position"] for i in range(len(self.nodes))] , dtype=str)
        pts = np.array([self.nodes[i]["point"] for i in range(len(self.nodes))])
        ii = np.arange(len(pts))
        deleteindex = []
        indexes = np.where(pos[:] == "b")[0]
        for ix in indexes:
            if np.any(ix == deleteindex):
                continue
            pb = np.where((np.abs(pts[:,0] - pts[ix,0]) < self.eps[0] ) & (np.abs(pts[:,1] - pts[ix,1]) < self.eps[1] ) & (ii[:] != ix))[0]
            deleteindex.extend(pb)
        self.nodes = [self.nodes[i] for i in range(len(self.nodes)) if i not in deleteindex]



    def judgeInDomain(self):
        self.domain.deleteOutDomain(self.nodes)
        self.nodes = [self.nodes[i] for i in range(len(self.nodes)) if self.nodes[i]["position"] != "nd"]
        self.domain.deleteOutDomain(self.nodes)
       
    def sort(self, epsilon=10):
        self.nodes = sorted(self.nodes, key=lambda x: [np.round(x["point"][1], 8),np.round(x["point"][0], 8)])

    def setNextNo(self):
        # border
        self.domain.getNextNode(self.nodes)
        
        # another
        pt  = np.array([node["point"] for node in self.nodes])
        for x in self.xs:
           x_index = np.where(np.isclose(pt[:,0], x))[0]
           for x_index_i in range(len(x_index)):
               nn = self.nodes[x_index[x_index_i]]["nextnode"]
               nnl = [nn[n]["no"] for n in range(len(nn))]
               if (x_index_i != 0) and (np.all(nnl != x_index[x_index_i-1])):
                   self.nodes[x_index[x_index_i]]["nextnode"].append({"no": x_index[x_index_i - 1], "position": "d" } )
               if (x_index_i != len(x_index)-1) and (np.all(nnl != x_index[x_index_i+1])):
                   self.nodes[x_index[x_index_i]]["nextnode"].append({"no": x_index[x_index_i + 1], "position": "u" } )

        for y in self.ys:
           y_index = np.where(np.isclose(pt[:,1], y))[0]
           for y_index_i in range(len(y_index)):
               nn = self.nodes[y_index[y_index_i]]["nextnode"]
               nnl = [nn[n]["no"] for n in range(len(nn))]
               if (y_index_i != 0) and (np.all(nnl != y_index[y_index_i-1])):
                   self.nodes[y_index[y_index_i]]["nextnode"].append({"no": y_index[y_index_i - 1], "position": "l" } )
               if (y_index_i != len(y_index)-1) and (np.all(nnl != y_index[y_index_i+1])):
                   self.nodes[y_index[y_index_i]]["nextnode"].append({"no": y_index[y_index_i + 1], "position": "r" } )
         
    def print(self):
        np.set_printoptions(precision = 3)
        for i, nodes in enumerate(self.nodes):
            print("node"+str(i), nodes)