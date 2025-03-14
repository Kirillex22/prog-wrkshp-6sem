from lab1.hashers import Hashers
import math

class HyperLogLog:
    def __init__(self, b):
        self.b = b
        self.m = 1 << b
        self.data = [0] * self.m
        self.alphaMM = (0.7213 / (1 + 1.079 / self.m)) * self.m * self.m

    def _hash(self, x):
        return Hashers.djb2(str(x))

    def add(self, item):
        x = self._hash(item)
        j = x & (self.m - 1)
        w = x >> self.b
        self.data[j] = max(self.data[j], self._rho(w))

    def _rho(self, w):
        if w == 0:
            return 0
        return (w ^ (1 << w.bit_length() - 1)).bit_length() + 1

    def estimate(self):
        Z = 1.0 / sum([0.5**reg for reg in self.data])
        E = self.alphaMM * Z
        if E <= 2.5 * self.m:
            V = self.data.count(0)
            if V > 0:
                E = self.m * math.log(self.m / V)
        return E

