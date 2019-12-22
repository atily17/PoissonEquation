import numpy as np

import time
from Problem import Problem
from Grid import Grid
from Solver import Solver
from Result import Result

class PoissonEquation:
    def __init__(self, domain, source):
        self.problem = Problem.Problem()
        self.problem.setDomain(**domain)
        self.problem.setSource(**source)

    def generateGrid(self, grid, mode="All"):
        self.grid = Grid.Grid(self.problem, **grid)

    def solve(self, method):
        solve = Solver.Solver()
        if method == "FDM":
            self.solution = solve.FDM(self.problem, self.grid)

    def result(self):
        self.result = Result.Result(self.solution, self.grid, self.problem)
        self.result.calcDensityFlux()

    def plot(self, type):
        if type == "domain":
            self.problem.domain.plot()
        elif type == "grid":
            self.grid.plot()
        elif type == "Potential":
            self.result.plot("Potential")
        elif type == "DensityFlux":
            self.result.plot("DensityFlux")

    def print(self, type):
        if type == "problem":
            self.problem.print()
    

if __name__ == "__main__":
    domain = {"shape":"Polygon",
              "vertexes":[[-1,-1],[1,-1], [0.4,1],[-0.4,1]],
              "bc":{
                  "bc": [
                      {"bctype":"Dirichlet", "constant":-1}, 
                      {"bctype":"Neumann", "constant":0},
                      {"bctype":"Dirichlet", "constant":1},
                      {"bctype":"Neumann", "constant":0}
                      ], 
                  "priority":[0,2,1,3]
                  }
              }
    source = {"source": 0}
    grid = {"type":"Cartesian", "div":[25,25]}
    method = "FDM"

    print("Problem")
    t1 = time.time()
    poisson = PoissonEquation(domain,source)
    t2 = time.time()
    print(t2 - t1)

    print("Generate Grid")
    t1 = time.time()
    poisson.generateGrid(grid, "Node")
    t2 = time.time()
    print(t2 - t1)

    print("solve")
    t1 = time.time()
    poisson.solve(method)
    t2 = time.time()
    print(t2 - t1)

    poisson.result()
    poisson.plot("Potential")
    poisson.plot("DensityFlux")