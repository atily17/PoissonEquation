from . import MatrixGenerater
from . import VectorGenerater
import numpy as np

class FDM(object):
    def __init__(self):
        pass

    def solve(self, problem, grid):
        matrix = MatrixGenerater.MatrixGenerater().generate(problem, grid,"CartesianGrid")
        vector = VectorGenerater.VectorGenerater().generate(problem, grid)

        return np.linalg.solve(matrix, vector)