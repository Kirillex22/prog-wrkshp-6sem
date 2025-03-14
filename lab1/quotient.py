from hashers import *

class QuotientFilter:
    def __init__(self, size=1024, q_bits=4):
        self.size = size
        self.q_bits = q_bits
        self.table = [None] * size

    def _hash(self, item):
        h = Hashers.djb2(item)
        quotient = h >> self.q_bits
        remainder = h & ((1 << self.q_bits) - 1)
        return quotient, remainder

    def add(self, item):
        quotient, remainder = self._hash(item)
        index = quotient % self.size
        self.table[index] = remainder

    def contains(self, item):
        quotient, remainder = self._hash(item)
        index = quotient % self.size
        return self.table[index] == remainder





