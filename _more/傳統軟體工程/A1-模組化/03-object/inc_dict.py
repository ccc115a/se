def inc(o):
    o['n'] = o['n']+1

x = {'n':1}
inc(x)
inc(x)
print(x)
