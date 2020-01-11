from . import FDM
from . import FEM

class Solver(object):
    def __init__(self):
        pass

    def FDM(self, problem, grid):
        fdm = FDM.FDM()
        solution = fdm.solve(problem, grid)
        return {"solution": solution, "quantity":"Potential"}

    def FEM(self, problem, grid):
        fem = FEM.FEM()
        solution = fem.solve(problem, grid)
        return {"solution": solution, "quantity":"Potential"}