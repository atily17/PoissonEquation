from . import MatrixGenerater
from . import VectorGenerater
import numpy as np

class FEM(object):
    def __init__(self):
        pass

    def solve(self, problem, grid):
        matrix = MatrixGenerater.MatrixGenerater().generate(problem, grid,"CartesianGrid")
        #vector = VectorGenerater.VectorGenerater().generate(problem, grid)


        #for i in range(len(vector)):
        #    print(vector[i])
        #x = matrix != 0
        #for i in range(len(matrix)):
        #    print(matrix[i])
        #    print(x[i])


        #return np.linalg.solve(matrix, vector)