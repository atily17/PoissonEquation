import numpy as np

import time
import Problem
import Grid
import Solver
import Result

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

    def plot(self, plotType = "all"):
        if plotType == "all" or plotType == "Domain":
            self.problem.domain.plot()
        if plotType == "all" or plotType == "Grid":
            self.grid.plot()
        if plotType == "all" or plotType == "Potential":
            self.result.plot("Potential")
        if plotType == "all" or plotType == "DensityFlux":
            self.result.plot("DensityFlux")

    def print(self, printType = "all"):
        if printType == "all" or printType == "Problem":
            self.problem.print()
        if printType == "all" or printType == "Grid":
            self.grid.print()
        if printType == "all" or printType == "result":
            self.result.print()

        if printType == "Domain" or printType == "Source":
            self.problem.print(printType)
        elif printType == "Node":
            self.grid.print(printType)
        elif printType == "Potential" or printType == "FluxDensity":
            self.grid.print(printType)

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

    poisson.print()