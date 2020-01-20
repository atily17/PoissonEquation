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
        if mode == "FDM":
            self.grid = Grid.Grid(self.problem, grid, "FDM")
        if mode == "FEM":
            self.grid = Grid.Grid(self.problem, grid, "FEM")

    def solve(self, method):
        solve = Solver.Solver()
        if method == "FDM":
            self.solution = solve.FDM(self.problem, self.grid)
        if method == "FEM":
            self.solution = solve.FEM(self.problem, self.grid)

    def result(self):
        self.result = Result.Result(self.solution, self.grid, self.problem)
        #self.result.calcFluxDensity()

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
        if printType == "all" or printType == "Result":
            self.result.print()

        if printType == "Domain" or printType == "Source":
            self.problem.print(printType)
        elif printType == "Node":
            self.grid.print(printType)
        elif printType == "Potential" or printType == "FluxDensity":
            self.grid.print(printType)


if __name__ == "__main__":
    filename = "./Example/Problem4.json"
    problem = IOData.InputData().readProblemData(filename)

    #problem["source"] = lambda x: (-10 if ((-0.2 < x[0] < 0.2) and (-0.2 < x[1] < 0.2)) else 0)

    grid = {"node":{
                "type":"Cartesian",
                "div":[50,50]
                }, 
            "cell":{
                "type":"Triangle"
                }
            }
    method = "FEM"

    print("Problem")
    t1 = time.time()
    poisson = PoissonEquation(problem)
    t2 = time.time()
    print(t2 - t1)

    print("Generate Grid")
    t1 = time.time()
    poisson.generateGrid(grid, method)
    t2 = time.time()
    print(t2 - t1)
    #poisson.plot("Grid")
    
    print("solve")
    t1 = time.time()
    poisson.solve(method)
    t2 = time.time()
    print(t2 - t1)

    poisson.result()
    poisson.plot("Potential")
    poisson.plot("FluxDensity")

    ##poisson.print()
    #filename = "./potential.json"
    #IOData.OutputData().writeFluxDensity(poisson.result.fluxDensity.fluxDensity, filename)
