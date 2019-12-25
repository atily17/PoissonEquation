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

            for nextnode in self.nodes[i]["nextnode"]:
                if nextnode["position"] == "l":
                    l_index = nextnode["no"]
                    dxl = self.nodes[i]["point"][0] - self.nodes[l_index]["point"][0]
                elif nextnode["position"] == "r":
                    r_index = nextnode["no"]
                    dxr = self.nodes[r_index]["point"][0] - self.nodes[i]["point"][0]
                elif nextnode["position"] == "d":
                    d_index = nextnode["no"]
                    dxd = self.nodes[i]["point"][1] - self.nodes[d_index]["point"][1]
                elif nextnode["position"] == "u":
                    u_index = nextnode["no"]
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
        nextNodePoint = np.array([self.nodes[nextNode[j]["no"]]["point"] for j in range(len(nextNode))])
        nextNodeVec = nextNodePoint - self.nodes[i]["point"]
        nextNodePos = [nN["position"] for nN in nextNode ]
        # 内積と外積
        dot = nextNodeVec[:,0] * normalVec[0] + nextNodeVec[:,1] * normalVec[1]
        cross = normalVec[0] * nextNodeVec[:,1] - normalVec[1] * nextNodeVec[:,0]

        # cornerのとき
        if self.nodes[i]["position"][0] == "c":
            p0 = self.domain.vertexes[ int(self.nodes[i]["position"][1:])]
            p1 = self.domain.vertexes[(int(self.nodes[i]["position"][1:]) + 1) % self.domain.nVertexes]
            p2 = self.domain.vertexes[(int(self.nodes[i]["position"][1:]) - 1) % self.domain.nVertexes]
            vec1 = (p1 - p0) / np.linalg.norm(p1 - p0, ord=2)
            vec2 = (p0 - p2) / np.linalg.norm(p2 - p0, ord=2)
            normalVec1 = np.dot(np.array([[0, -1],[1, 0]]), vec1)
            normalVec2 = np.dot(np.array([[0, -1],[1, 0]]), vec2)
            normalVec = (np.linalg.norm(normalVec2)*normalVec1 + np.linalg.norm(normalVec1)*normalVec2 )
            normalVec /= (np.linalg.norm(normalVec1) + np.linalg.norm(normalVec2))
            normalVec /= np.linalg.norm(normalVec, ord=2)

        if self.nodes[i]["position"][0] == "c" and len(nextNode) == 2:
            backNum = nextNodePos.index("b")
            fwrdNum = nextNodePos.index("f")
            backIndex = nextNode[backNum]["no"]
            fwrdIndex = nextNode[fwrdNum]["no"]
            mtrix = np.array([nextNodeVec[backNum], nextNodeVec[fwrdNum]]).T
            ans = np.linalg.solve(mtrix, normalVec)
            self.matrix[i][i] = - ans[0] - ans[1]
            self.matrix[i][backIndex] = ans[0]
            self.matrix[i][fwrdIndex]  = ans[1]

        # borderのとき
        elif len(nextNode) > 2:
            temp = nextNodePos[:]
            temp.remove("b")
            temp.remove("f")
            tt = temp[0]

            i1 = nextNodePos.index("b")
            p1 = nextNode[i1]["no"]
            x1 = nextNodeVec[i1]
            if np.linalg.norm(x1) < (np.linalg.norm(np.array(self.eps))):
                nnextbNode = self.nodes[p1]["nextnode"]
                nnextbNodePos = [nnextbNode[j]["position"] for j in range(len(nnextbNode))]
                nnextbNodePoint = np.array([self.nodes[nnextbNode[j]["no"]]["point"] for j in range(len(nnextbNode))])
                nnextbNodeVec = nnextbNodePoint - self.nodes[i]["point"]
                i1 = nnextbNodePos.index("b")
                p1 = nnextbNode[i1]["no"]
                x1 = nnextbNodeVec[i1]
            
            i2 = nextNodePos.index("f")
            p2 = nextNode[i2]["no"]
            x2 = nextNodeVec[i2]
            if np.linalg.norm(x2) < (np.linalg.norm(np.array(self.eps))):
                nnextfNode = self.nodes[p2]["nextnode"]
                nnextfNodePos = [nnextfNode[j]["position"] for j in range(len(nnextfNode))]
                nnextfNodePoint = np.array([self.nodes[nnextfNode[j]["no"]]["point"] for j in range(len(nnextfNode))])
                nnextfNodeVec = nnextfNodePoint - self.nodes[i]["point"]
                i2 = nnextfNodePos.index("f")
                p2 = nnextfNode[i2]["no"]
                x2 = nnextfNodeVec[i2]

            x3 = nextNodeVec[nextNodePos.index(tt)]
            p3 = nextNode[nextNodePos.index(tt )]["no"]

            row1 = [x1[0], x2[0], x3[0], 0, 0]
            row2 = [x1[1], x2[1], x3[1], 0, 0]
            row3 = [x1[0]*x1[0], x2[0]*x2[0], x3[0]*x3[0], -2*normalVec[0], 0]
            row4 = [x1[0]*x1[1], x2[0]*x2[1], x3[0]*x3[1], -normalVec[1]  , -normalVec[0]]
            row5 = [x1[1]*x1[1], x2[1]*x2[1], x3[1]*x3[1], 0, -2*normalVec[1]]

            mtrix = np.array([row1, row2, row3, row4, row5])
            normalVec = [normalVec[0], normalVec[1], 0, 0, 0]
            ans = np.linalg.solve(mtrix, normalVec)
            self.matrix[i][i] = - ans[0] - ans[1] - ans[2]
            self.matrix[i][p1] = ans[0]
            self.matrix[i][p2] = ans[1]
            self.matrix[i][p3] = ans[2]
