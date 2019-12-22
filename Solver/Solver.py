from . import FDM

class Solver(object):
    def __init__(self):
        pass

    def FDM(self, problem, grid):
        fdm = FDM.FDM()
        solution = fdm.solve(problem, grid)
        return {"solution": solution, "quantity":"Potential"}