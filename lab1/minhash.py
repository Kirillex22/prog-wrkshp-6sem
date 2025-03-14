import numpy as np
import random


class MinHash:
    def __init__(self, num_hashes):
        self.num_hashes = num_hashes
        self.hash_funcs = []

    def _generate_hash_functions(self, max_value):
        prime = self._next_prime(max_value)
        self.hash_funcs = [(random.randint(1, prime - 1), random.randint(0, prime - 1)) for _ in range(self.num_hashes)]

    def _hash(self, x, a, b, p):
        return (a * x + b) % p

    def compute_signatures(self, sets):
        unique_elements = list(set().union(*sets))
        element_index = {elem: idx for idx, elem in enumerate(unique_elements)}
        num_elements = len(unique_elements)

        self._generate_hash_functions(num_elements)
        prime = self._next_prime(num_elements)
        signatures = np.full((self.num_hashes, len(sets)), np.inf)

        for set_idx, s in enumerate(sets):
            for elem in s:
                elem_idx = element_index[elem]
                for i, (a, b) in enumerate(self.hash_funcs):
                    hash_val = self._hash(elem_idx, a, b, prime)
                    signatures[i, set_idx] = min(signatures[i, set_idx], hash_val)

        return signatures

    def jaccard_similarity(self, sig1, sig2):
        return np.mean(sig1 == sig2)

    @staticmethod
    def is_prime(k):
        if k < 2:
            return False
        for i in range(2, int(np.sqrt(k)) + 1):
            if k % i == 0:
                return False
        return True

    def _next_prime(self, n):
        prime = n
        while not MinHash.is_prime(prime):
            prime += 1
        return prime