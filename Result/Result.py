from . import Potential
from . import DensityFlux

class Result(object):
    def __init__(self, solution, grid, problem):
        self.grid = grid
        self.solution = solution
        self.problem = problem
        if solution["quantity"] == "Potential":
            self.potentials = Potential.Potential(solution["solution"], grid)

    def calcDensityFlux(self):
        if self.potentials is not None:
            self.densityFlux = DensityFlux.DensityFlux(self.grid)
            self.densityFlux.calcDensityFlux(self.potentials.potentials)

    def print(self):
        self.potentials.print()

    def plot(self, quantity):
        if quantity == "Potential":
            self.potentials.plot(self.problem)
            self.print()
        if quantity == "DensityFlux":
            self.densityFlux.plot(self.problem)
