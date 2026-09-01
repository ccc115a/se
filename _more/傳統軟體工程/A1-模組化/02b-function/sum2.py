def sum(n):
    s = 0
    for i in range(1, n+1):
        s += i
    return s

print('sum(10)=', sum(10))
print('sum(100)=', sum(100))
