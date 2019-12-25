import json
import os

class InputData(object):
    def readProblemData(self, filename):
        filepath = os.path.dirname(os.path.abspath(__file__))
        filepath = os.path.normpath(os.path.join(filepath, "../"+filename))
        with open(filepath, mode = "r", encoding="utf_8_sig") as fp:
            problem = json.load(fp)
        return problem