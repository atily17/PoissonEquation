
import numpy as np

class Source(object):
    def __init__(self, source):
        if isinstance(source, (int, float)):
            self.source = lambda x: source
        else:
            self.source = source

    def print(self):
        print("-----Source-----")
        print("n_vertexes", self.source)