from . import Domain
from . import Source

class Problem(object):
    def __init__(self, problem):
        self.setDomain(**problem["domain"])
        self.setSource(problem["source"])

    # "shape:"
    def setDomain(self, **domain):
        assert len(domain["vertexes"]) == len(domain["bc"]["bc"]), "it must be len(domain['vertexes']) == len(domain['bc']['bc'])"
        if domain["shape"]=="Polygon":
            self.domain=Domain.Polygon(domain["vertexes"], domain["bc"])
            self.domain.calcRange()
    def setSource(self, source):
        self.source=Source.Source(source)

    def print(self, printType = "all"):
        print("-----Problem-----")
        if printType == "all" or printType =="Domain":
            self.domain.print()
        if printType == "all" or printType =="Source":
            self.source.print()