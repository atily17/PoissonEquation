from . import Potential
from . import FluxDensity

class Result(object):
    def __init__(self, solution, grid, problem):
        self.grid = grid
        self.solution = solution
        self.problem = problem
        if solution["quantity"] == "Potential":
            self.potentials = Potential.Potential(solution["solution"], grid)

    def calcFluxDensity(self):
        if self.potentials is not None:
            self.fluxDensity = FluxDensity.FluxDensity(self.grid)
            self.fluxDensity.calcFluxDensity(self.potentials.potentials)

    def print(self, valueType = "all"):
        print("-----Result-----")
        if valueType == "all" or valueType == "Potential":
            self.potentials.print()
        if valueType == "all" or valueType == "FluxDensity":
            self.fluxDensity.print()

    def plot(self, valueType = "all"):
        if valueType == "all" or valueType == "Potential":
            self.potentials.plot(self.problem)
        if valueType == "all" or valueType == "FluxDensity":
            self.fluxDensity.plot(self.problem)
