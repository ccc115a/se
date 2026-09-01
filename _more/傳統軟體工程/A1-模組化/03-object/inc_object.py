class Int:
    def __init__(self, n):
        self.n = n
    def inc(self):
        self.n = self.n+1
    def __str__(self):
        return str(self.n)

x = Int(1)
x.inc()
x.inc()
print('x=', x)