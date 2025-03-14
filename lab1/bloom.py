import numpy as np

from hashers import Hashers


class BloomFilter:
    def __init__(self, size, element_limit = 5000, hfc = None):
        self.element_limit = element_limit
        self.size = size
        self.hash_func = Hashers.djb2
        self.filter = np.zeros(self.size, dtype=bool)
        if not hfc:
            self.hash_func_cnt = round(self.size/element_limit * np.log(2))
        else:
            self.hash_func_cnt = hfc

    def clear(self):
        self.filter = np.zeros(self.size, dtype=bool)


    def set_hash_func(self, hash_func) -> None:
        self.hash_func = hash_func


    def hash(self, element, order):
        return self.hash_func(str(order) + element) % self.size


    def add(self, element) -> None:
        for i in range(self.hash_func_cnt):
            self.filter[self.hash(element, i)] = True


    def contains(self, element) -> bool:
        for i in range(self.hash_func_cnt):
            if not self.filter[self.hash(element, i)]:
                return False
        return True


    def __or__(self, bloom):
        new_filter = np.logical_or(self.filter, bloom.filter)
        new_bloom = BloomFilter(self.size, self.element_limit)
        new_bloom.hash_func = self.hash_func
        new_bloom.filter = new_filter
        return new_bloom


    def __and__(self, bloom):
        new_filter = np.logical_and(self.filter, bloom.filter)
        new_bloom = BloomFilter(self.size, self.element_limit)
        new_bloom.hash_func = self.hash_func
        new_bloom.filter = new_filter
        return new_bloom


class CounterBF(BloomFilter):
    def __init__(self, size, element_limit=5000, hfc = None):
        super().__init__(size, element_limit, hfc)
        self.counter = np.zeros(self.size, dtype=int)


    def add(self, element):
        for i in range(self.hash_func_cnt):
            self.filter[self.hash(element, i)] = True
            self.counter[i] += 1


    def remove(self, element):
        for i in range(self.hash_func_cnt):
            if not self.counter[self.hash(element, i)] > 0:
                self.counter[self.hash(element, i)] -= 1
                self.filter[self.hash(element, i)] = False


    def __or__(self, bloom):
        new_filter = np.logical_or(self.filter, bloom.filter)
        new_counter = self.counter + bloom.counter
        new_bloom = BloomFilter(self.size, self.element_limit)
        new_bloom.hash_func = self.hash_func
        new_bloom.filter = new_filter
        new_bloom.counter = new_counter
        return new_bloom


    def __and__(self, bloom):
        new_filter = np.logical_and(self.filter, bloom.filter)
        new_counter = np.minimum(self.counter, bloom.counter)
        new_bloom = BloomFilter(self.size, self.element_limit)
        new_bloom.hash_func = self.hash_func
        new_bloom.filter = new_filter
        new_bloom.counter = new_counter
        return new_bloom