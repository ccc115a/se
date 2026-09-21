def sum(n):
    s = 0
    i = 1
    while i<=n:
        s += i
        i += 1
    return s

print('sum(10)=', sum(10))
print('sum(100)=', sum(100))