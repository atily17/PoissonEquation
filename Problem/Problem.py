from . import Domain
from . import Source

class Problem(object):
    def __init__(self):
        pass

    # "shape:"
    def setDomain(self, **domain):
        if domain["shape"]=="Polygon":
            self.domain=Domain.Polygon(domain["vertexes"], domain["bc"])
            self.domain.calcRange()
    def setSource(self, **source):
        self.source=Source.Source(source["source"])
