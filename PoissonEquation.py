import time
import numpy as np


import Problem
import Grid
import Solver
import Result
import IOData

class PoissonEquation:
    def __init__(self, problem):
        self.problem = Problem.Problem(problem)

    def generateGrid(self, grid, mode="All"):
        self.grid = Grid.Grid(self.problem, **grid)

    def solve(self, method):
        solve = Solver.Solver()
        if method == "FDM":
            self.solution = solve.FDM(self.problem, self.grid)

    def result(self):
        self.result = Result.Result(self.solution, self.grid, self.problem)
        self.result.calcFluxDensity()

    def plot(self, plotType = "all"):
        if plotType == "all" or plotType == "Domain":
            self.problem.domain.plot()
        if plotType == "all" or plotType == "Grid":
            self.grid.plot()
        if plotType == "all" or plotType == "Potential":
            self.result.plot("Potential")
        if plotType == "all" or plotType == "FluxDensity":
            self.result.plot("FluxDensity")

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


def dipole(x):
        z = 0
        if ((-0.1 < x[0] < 0) and (-0.1 < x[1] < 0)):
            z = 1
        elif ((0 < x[0] < 0.1) and (0 < x[1] < 0.1)):
            z = -1
        return z

if __name__ == "__main__":
    filename = "./Example/Problem1.json"
    problem = IOData.InputData().readProblemData(filename)

    #if put charge(=-5) on center
    #problem["source"] = lambda x: (-10 if ((-0.2 < x[0] < 0.2) and (-0.2 < x[1] < 0.2)) else 0)
    problem["source"] = dipole

    grid = {"type":"Cartesian", "div":[100,100]}
    method = "FDM"

    print("Problem")
    t1 = time.time()
    poisson = PoissonEquation(problem)
    t2 = time.time()
    print(t2 - t1)

    print("Generate Grid")
    t1 = time.time()
    poisson.generateGrid(grid, "Node")
    t2 = time.time()
    print(t2 - t1)
    poisson.plot("Grid")

    print("solve")
    t1 = time.time()
    poisson.solve(method)
    t2 = time.time()
    print(t2 - t1)

    poisson.result()
    poisson.plot("Potential")
    poisson.plot("FluxDensity")

    #poisson.print()
    filename = "./potential.json"
    IOData.OutputData().writeFluxDensity(poisson.result.fluxDensity.fluxDensity, filename)