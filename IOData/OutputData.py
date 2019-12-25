import json
import os

class OutputData(object):
    def writePotential(self, potential, filename):
        potentials = [{ "potential":potential[i]["potential"], "point":list(potential[i]["point"])} for i in range(len(potential))]
        dict = {"potential": potentials}
        filepath = os.path.dirname(os.path.abspath(__file__))
        filepath = os.path.normpath(os.path.join(filepath, "../"+filename))
        with open(filepath, mode = "w", encoding="utf_8_sig") as fp:
            problem = json.dump(dict, fp, indent=4)


    def writeFluxDensity(self, fluxDensity, filename):
        fluxDensity = [{"Dx":fluxDensity[i]["Dx"],
                        "Dy":fluxDensity[i]["Dy"],
                        "intensity":fluxDensity[i]["intensity"],
                        "point":list(fluxDensity[i]["point"]) } for i in range(len(fluxDensity))]
        dict = {"flux_density": fluxDensity}
        filepath = os.path.dirname(os.path.abspath(__file__))
        filepath = os.path.normpath(os.path.join(filepath, "../"+filename))
        with open(filepath, mode = "w", encoding="utf_8_sig") as fp:
            problem = json.dump(dict, fp, indent=4)