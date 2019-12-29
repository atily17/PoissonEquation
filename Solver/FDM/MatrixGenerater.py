import numpy as np
import copy

class MatrixGenerater(object):
    def generate(self, problem, grid, case="Any"):
        self.eps = grid.node.eps
        self.nodes = grid.node.nodes
        self.bc = problem.domain.bc
        self.domain = problem.domain
        if case == "CartesianGrid":
            return self.caseCartesianGrid()

    def caseCartesianGrid(self):
        self.matrix = np.zeros((len(self.nodes), len(self.nodes)))
        for i in range(len(self.nodes)):
            if self.nodes[i]["position"] != "in":
                self.border(i)
                continue

            
            l_index = self.nodes[i]["nextnode"]["l"]
            dxl = self.nodes[i]["point"][0] - self.nodes[l_index]["point"][0]
            
            r_index = self.nodes[i]["nextnode"]["r"]
            dxr = self.nodes[r_index]["point"][0] - self.nodes[i]["point"][0]
            
            d_index = self.nodes[i]["nextnode"]["d"]
            dxd = self.nodes[i]["point"][1] - self.nodes[d_index]["point"][1]
            
            u_index = self.nodes[i]["nextnode"]["u"]
            dxu = self.nodes[u_index]["point"][1] - self.nodes[i]["point"][1]
            
            self.matrix[i][l_index] = 2 * (1 / (dxl + dxr)) * (1 / dxl)
            self.matrix[i][r_index] = 2 * (1 / (dxl + dxr)) * (1 / dxr)
            self.matrix[i][d_index] = 2 * (1 / (dxd + dxu)) * (1 / dxd)
            self.matrix[i][u_index] = 2 * (1 / (dxd + dxu)) * (1 / dxu)
            self.matrix[i][i] = - (self.matrix[i][l_index] + self.matrix[i][r_index] + self.matrix[i][d_index] + self.matrix[i][u_index])
        np.set_printoptions(precision = 2, threshold = 10000, linewidth = 10000)
        print(self.matrix)
        return self.matrix

    def border(self, i):
        assert (self.nodes[i]["position"][0] == "b" or self.nodes[i]["position"][0] == "c"), self.nodes[i]["position"]
        if self.nodes[i]["position"][0] == "b":
            t = int(self.nodes[i]["position"][1])
            bctype = self.bc["bc"][t]["bctype"]
        elif self.nodes[i]["position"][0] == "c":
            t = int(self.nodes[i]["position"][1])
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
            self.Neumann(i, t)
        elif bctype == "Dirichlet":
            self.Dirichlet(i)

    def Dirichlet(self, i):
        self.matrix[i][i] = 1


    def Neumann(self, i, t):
        # 境界のベクトル
        p1 = self.domain.vertexes[t]
        p2 = self.domain.vertexes[(t + 1) % self.domain.nVertexes]
        vec = (p2 - p1) / np.linalg.norm(p2 - p1, ord=2)
        normalVec = np.dot(np.array([[0, -1],[1, 0]]), vec)
        # nextnode
        nextNode = self.nodes[i]["nextnode"]
        nextNodePoint = { k: np.array(self.nodes[v]["point"]) for k,v in nextNode.items() }
        nextNodeVec = { k: nextNodePoint[k] - self.nodes[i]["point"] for k,v in nextNode.items() }
        # 内積と外積
        dot = { k: nextNodeVec[k][0] * normalVec[0] + nextNodeVec[k][1] * normalVec[1] for k,v in nextNode.items() }
        cross = { k: normalVec[0] * nextNodeVec[k][1] - normalVec[1] * nextNodeVec[k][0] for k,v in nextNode.items() }

        # cornerのとき
        if self.nodes[i]["position"][0] == "c":
            p0 = self.domain.vertexes[int(self.nodes[i]["position"][1:])]
            p1 = self.domain.vertexes[(int(self.nodes[i]["position"][1:]) + 1) % self.domain.nVertexes]
            p2 = self.domain.vertexes[(int(self.nodes[i]["position"][1:]) - 1) % self.domain.nVertexes]
            vec1 = (p1 - p0) / np.linalg.norm(p1 - p0, ord=2)
            vec2 = (p0 - p2) / np.linalg.norm(p2 - p0, ord=2)
            normalVec1 = np.dot(np.array([[0, -1],[1, 0]]), vec1)
            normalVec2 = np.dot(np.array([[0, -1],[1, 0]]), vec2)
            normalVec = (np.linalg.norm(normalVec2) * normalVec1 + np.linalg.norm(normalVec1) * normalVec2)
            normalVec /= (np.linalg.norm(normalVec1) + np.linalg.norm(normalVec2))
            normalVec /= np.linalg.norm(normalVec, ord=2)

        if self.nodes[i]["position"][0] == "c" and len(nextNode) == 2:
            backIndex = nextNode["b"]
            fwrdIndex = nextNode["f"]
            mtrix = np.array([nextNodeVec["b"], nextNodeVec["f"]]).T
            ans = np.linalg.solve(mtrix, normalVec)
            self.matrix[i][i] = - ans[0] - ans[1]
            self.matrix[i][backIndex] = ans[0]
            self.matrix[i][fwrdIndex] = ans[1]

        # borderのとき
        elif len(nextNode) > 2:
            p1 = nextNode["b"]
            x1 = nextNodeVec["b"]
            if np.linalg.norm(x1) < (np.linalg.norm(np.array(self.eps))):
                nnextbNode = self.nodes[p1]["nextnode"]["b"]
                nnextbNodePoint = np.array(self.nodes[nnextbNode]["point"])
                nnextbNodeVec = nnextbNodePoint - self.nodes[i]["point"]
                p1 = nnextbNode
                x1 = nnextbNodeVec
            
            p2 = nextNode["f"]
            x2 = nextNodeVec["f"]
            if np.linalg.norm(x2) < (np.linalg.norm(np.array(self.eps))):
                nnextfNode = self.nodes[p2]["nextnode"]["f"]
                nnextfNodePoint = np.array(self.nodes[nnextfNode]["point"])
                nnextfNodeVec = nnextfNodePoint - self.nodes[i]["point"]
                p2 = nnextfNode
                x2 = nnextfNodeVec
            
            p3, x3 = self.__searchBestNode(i,nextNode, normalVec)
            #keys = list(nextNode.keys())
            #keys.remove("f")
            #keys.remove("b")
            #key = keys[0]
            #p3 = nextNode[key]
            #x3 = nextNodeVec[key]

            row1 = [x1[0], x2[0], x3[0], 0, 0]
            row2 = [x1[1], x2[1], x3[1], 0, 0]
            row3 = [x1[0] * x1[0], x2[0] * x2[0], x3[0] * x3[0], -2 * normalVec[0], 0]
            row4 = [x1[0] * x1[1], x2[0] * x2[1], x3[0] * x3[1], -normalVec[1]  , -normalVec[0]]
            row5 = [x1[1] * x1[1], x2[1] * x2[1], x3[1] * x3[1], 0, -2 * normalVec[1]]

            mtrix = np.array([row1, row2, row3, row4, row5])
            normalVec = [normalVec[0], normalVec[1], 0, 0, 0]
            ans = np.linalg.solve(mtrix, normalVec)
            self.matrix[i][i] = - ans[0] - ans[1] - ans[2]
            self.matrix[i][p1] = ans[0]
            self.matrix[i][p2] = ans[1]
            self.matrix[i][p3] = ans[2]

    def __searchBestNode(self, i, nextNode, normalVec):
        temp1 = copy.deepcopy(nextNode)
        temp1.pop("f")
        temp1.pop("b")
        temp1= list(temp1.values())
        if len(temp1) != 0:
            nextValue = np.array([temp1[j] for j in range(len(temp1))])
            nextPoint = np.array([self.nodes[nextValue[j]]["point"] for j in range(len(nextValue))])
            nextVec   = (nextPoint - self.nodes[i]["point"])
            nextVec1  = nextVec/np.linalg.norm(nextVec, axis = 1)
            nextDot   = nextVec1[:,0] * normalVec[0] + nextVec1[:,1] * normalVec[1]
            nextIndex = np.argmax(nextDot)
            nextMax   = nextDot[nextIndex]
        else:
            nextMax   = 0

        nnextbNode = self.nodes[nextNode["b"]]["nextnode"]
        temp2 = copy.deepcopy(nnextbNode)
        temp2.pop("f")
        temp2.pop("b")
        temp2=list(temp2.values())
        if len(temp2) != 0:
            nnextbValue = np.array([temp2[j] for j in range(len(temp2))])
            nnextbPoint = np.array([self.nodes[nnextbValue[j]]["point"] for j in range(len(nnextbValue))])
            nnextbVec   = (nnextbPoint - self.nodes[i]["point"])
            nnextbVec1  = nnextbVec/np.linalg.norm(nnextbVec, axis = 1)
            nnextbDot   = nnextbVec1[:,0] * normalVec[0] + nnextbVec1[:,1] * normalVec[1]
            nnextbIndex = np.argmax(nnextbDot)
            nnextbMax   = nnextbDot[nnextbIndex]
        else:
            nnextbMax   = 0


        nnextfNode = self.nodes[nextNode["f"]]["nextnode"]
        temp3 = copy.deepcopy(nnextfNode)
        temp3.pop("f")
        temp3.pop("b")
        temp3=list(temp3.values())
        if len(temp3) != 0:
            nnextfValue = np.array([temp3[j] for j in range(len(temp3))])
            nnextfPoint = np.array([self.nodes[nnextfValue[j]]["point"] for j in range(len(nnextfValue))])
            nnextfVec   = (nnextfPoint - self.nodes[i]["point"])
            nnextfVec1  = nnextfVec/np.linalg.norm(nnextfVec, axis = 1)
            nnextfDot   = nnextfVec1[:,0] * normalVec[0] + nnextfVec1[:,1] * normalVec[1]
            nnextfIndex = np.argmax(nnextfDot)
            nnextfMax   = nnextfDot[nnextfIndex]
        else:
            nnextfMax   = 0

        if nnextfMax > nnextbMax and nnextfMax > nextMax:
            return nnextfValue[nnextfIndex], nnextfVec[nnextfIndex]

        elif nnextbMax > nnextfMax and nnextbMax > nextMax:
            return nnextbValue[nnextbIndex], nnextbVec[nnextbIndex]

        else:
            return nextValue[nextIndex], nextVec[nextIndex]