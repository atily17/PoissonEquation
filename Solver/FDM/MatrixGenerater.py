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
        dot = nextNodePoint[:,0] * normalVec[0] + nextNodePoint[:,1] * normalVec[1]
        cross = normalVec[0] * nextNodePoint[:,1] - normalVec[1] * nextNodePoint[:,0]

        # 境界が垂直のとき
        iszero = np.isclose(cross, 0)
        if np.any(iszero):
            ind = np.where(iszero)[0][0]
            pos = nextNode[ind]["position"]
            num = nextNode[ind]["no"]
            delta = self.nodes[num]["point"] - self.nodes[i]["point"]
            if pos == "l":
                self.matrix[i][i] = 1 / delta[0]
                self.matrix[i][num] = -1 / delta[0]
            elif pos == "d":
                self.matrix[i][i] = 1 / delta[1]
                self.matrix[i][num] = -1 / delta[1]
            elif pos == "r" :
                self.matrix[i][i] = -1 / delta[0]
                self.matrix[i][num] = 1 / delta[0]
            elif pos == "u":
                self.matrix[i][i] = -1 / delta[1]
                self.matrix[i][num] = 1 / delta[1]
            else:
                assert(1)
            return
        
        # cornerのとき
        if self.nodes[i]["position"][0] == "c":
            mtrix = np.array([nextNodeVec[nextNodePos.index("b")], nextNodeVec.index("f")]).T
            ans = np.linalg.solve(mtrix, normalVec)
            self.matrix[i][i] = - ans[0] - ans[1]
            self.matrix[i][minusNode] = ans[0]
            self.matrix[i][plusNode]  = ans[1]

        # borderのとき
        elif self.nodes[i]["position"][0] == "b":
            temp = nextNodePos[:]
            temp.remove("b")
            temp.remove("f")
            tt = temp[0]
            x1 = nextNodeVec[nextNodePos.index("b")]
            x2 = nextNodeVec[nextNodePos.index("f")]
            x3 = nextNodeVec[nextNodePos.index(tt)]

            p1 = nextNode[nextNodePos.index("b")]["no"]
            p2 = nextNode[nextNodePos.index("f")]["no"]
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