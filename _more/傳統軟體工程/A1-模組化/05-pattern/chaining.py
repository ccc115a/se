class Number:
    def __init__(self, value):
        self.value = value
    def add(self, b):
        return Number(self.value+b)
    def mul(self, b):
        return Number(self.value*b)
    def __str__(self):
        return str(self.value)

a = Number(3)
print('a.add(5).mul(2)=', a.add(5).mul(2))
print('a.add(5).mul(2).add(3).mul(3)=', a.add(5).mul(2).add(3).mul(3))