
import numpy as np

class Source(object):
    def __init__(self, source):
        print("-----Source-----")
        if isinstance(source, (int, float)):
            self.source = lambda x: source
        else:
            self.source = source