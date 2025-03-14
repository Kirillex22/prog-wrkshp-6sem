class Hashers:
    @staticmethod
    def djb2(s):
        hash = 5381
        for x in s:
            hash = ((hash << 5) + hash) + ord(x)
        return hash