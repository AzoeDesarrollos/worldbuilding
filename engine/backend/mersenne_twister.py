class Random:
    # Based on the work of Nils-Bernsdorf (2021)
    # https://github.com/yinengy/Mersenne-Twister-in-Python/
    def __init__(self, c_seed=0):
        # MT19937
        (self.w, self.n, self.m, self.r) = (32, 624, 397, 31)
        self.a = 0x9908B0DF
        (self.u, self.d) = (11, 0xFFFFFFFF)
        (self.s, self.b) = (7, 0x9D2C5680)
        (self.t, self.c) = (15, 0xEFC60000)
        self.l = 18
        self.f = 1812433253
        # make a arry to store the state of the generator
        self.MT = [0 for _ in range(self.n)]
        self.index = self.n + 1
        self.lower_mask = 0x7FFFFFFF
        self.upper_mask = 0x80000000
        # inital the seed
        self.c_seed = c_seed
        self.seed(c_seed)

    def seed(self, num):
        """initialize the generator from a seed"""
        self.MT[0] = num
        self.index = self.n
        for i in range(1, self.n):
            temp = self.f * (self.MT[i - 1] ^ (self.MT[i - 1] >> (self.w - 2))) + i
            self.MT[i] = temp & 0xffffffff

    def twist(self):
        """ Generate the next n values from the series x_i"""
        for i in range(0, self.n):
            x = (self.MT[i] & self.upper_mask) + \
                (self.MT[(i + 1) % self.n] & self.lower_mask)
            x_a = x >> 1
            if (x % 2) != 0:
                x_a = x_a ^ self.a
            self.MT[i] = self.MT[(i + self.m) % self.n] ^ x_a
        self.index = 0

    def extract_number(self):
        """ Extract a tempered value based on MT[index]
            calling twist() every n numbers
        """
        if self.index >= self.n:
            self.twist()

        y = self.MT[self.index]
        y = y ^ ((y >> self.u) & self.d)
        y = y ^ ((y << self.s) & self.b)
        y = y ^ ((y << self.t) & self.c)
        y = y ^ (y >> self.l)

        self.index += 1
        return y & 0xffffffff

    def random(self):
        """ return uniform ditribution in [0,1) """
        # a = (self.extract_number() / 10**8) % 1
        # return float('%.08f' % a)
        return self.extract_number() / 4294967296  # which is 2**w

    def randint(self, a, b):
        """ return random int in [a,b) """
        n = self.random()
        return int(n / (1 / (b - a)) + a)

    def shuffle(self, seq):
        """ shuffle the sequence """
        new_x = list(seq)
        for i in range(10 * len(seq)):
            a = self.randint(0, len(seq))
            b = self.randint(0, len(seq))
            new_x[a], new_x[b] = new_x[b], new_x[a]

        return new_x

    def choice(self, x, replace=True, size=1):
        """ choice an element randomly in the sequence 
            size: the number of element to be chosen
        """
        new_x = list(x)
        if size == 1:
            return new_x[self.randint(0, len(new_x))]
        else:
            if replace:
                return [new_x[self.randint(0, len(new_x))] for _ in range(size)]
            else:
                l = []
                for i in range(size):
                    if len(new_x) != 0:
                        a = self.randint(0, len(new_x))
                        l += [new_x[a]]
                        new_x.remove(new_x[a])
                return l

    def bern(self, p):
        """ generate a Bernoulli Random Variable
            p: the probability of True
        """
        return self.random() <= p

    def binomial(self, n, p):
        """ generate a Binomial Random Variable
            n: total times
            p: probability of success
        """
        a = [self.bern(p) for _ in range(n)]
        return a.count(True)

    def geometric(self, p):
        """ generate a Geometric Random Variable
            p: probability of success
        """
        u = self.random()
        b = 0
        k = 1
        while b < u:
            b += (1 - p) ** (k - 1) * p
            k += 1

        return k - 1


r = Random(0)

# method shortcuts
random = r.random
choice = r.choice
shuffle = r.shuffle
randint = r.randint

__all__ = [
    "random",
    "choice",
    "shuffle",
    "randint"
]