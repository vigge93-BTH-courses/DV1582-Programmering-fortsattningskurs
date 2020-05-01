class NumberSequence:
    def __init__(self, n):
        assert isinstance(n, int)
        assert n >= 0
        self._sequence = [0]*(n)
        self._pos = -1

    def __iter__(self):
        self._pos = -1
        return self.Iterator(self._sequence)

    def __getitem__(self, index):
        return self._sequence[index-1]

    class Iterator:
        def __init__(self, seq):
            self._pos = -1
            self._sequence = seq

        def __next__(self):
            self._pos += 1
            if self._pos == len(self._sequence):
                raise StopIteration
            return self._sequence[self._pos]


class Fibonacci(NumberSequence):
    def __init__(self, n):
        super().__init__(n)
        if n >= 1:
            self._sequence[0] = 1
        if n >= 2:
            self._sequence[1] = 1
        for i in range(2, n):
            self._sequence[i] = (self._sequence[i-1] + self._sequence[i-2])


class Catalan(NumberSequence):
    '''Determines the sequence of the n first Catalan numbers.'''

    def __init__(self, n):
        super().__init__(n)
        if n >= 1:
            self._sequence[0] = 1
        if n >= 2:
            self._sequence[1] = 1

        for i in range(2, n):
            for j in range(0, i):
                self._sequence[i] += self._sequence[j]*self._sequence[i-j-1]


class Primes(NumberSequence):
    def __init__(self, n):
        super().__init__(n)
        sequence_b = [True] * (n)
        p = 2
        while p * p <= n:
            if sequence_b[p-1] == True:
                # Update all multiples of p
                for i in range(p * 2, n + 1, p):
                    sequence_b[i-1] = False
            p += 1
        self._sequence = [idx+1 for idx, val in enumerate(sequence_b) if val]

    def is_prime(self, num):
        return num in self._sequence


if __name__ == "__main__":
    fib = Fibonacci(20)
    print(fib[6])
    cat = Catalan(20)
    print(cat[6])
    prim = Primes(100)
    print(prim.is_prime(3))
    print(prim[6])
    for f in fib:
        print(f)
