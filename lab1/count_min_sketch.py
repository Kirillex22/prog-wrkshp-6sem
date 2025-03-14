import numpy as np

from lab1.hashers import Hashers


class CountMinSketch:
    def __init__(self, linear_size, hfc):
        self.linear_size = linear_size
        self.hfc = hfc
        self.container = np.zeros((self.linear_size, self.hfc))
        self.hash_func = Hashers.djb2


    def _hash(self, element, order):
        try:
            return self.hash_func(str(order) + element)%self.linear_size
        except:
            print(element, order)


    def add(self, element):
        hashes = [self._hash(element, i) for i in range(self.hfc)]
        for i, v in enumerate(hashes):
            self.container[v][i] += 1


    def count(self, element):
        hashes = [self._hash(element, i) for i in range(self.hfc)]
        vals = [self.container[v][i] for i, v in enumerate(hashes)]
        return min(vals)