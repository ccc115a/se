from math import *

def df(f, x, dx=0.00001):
    return (f(x+dx)-f(x))/dx

print('df(sin, pi/4)=', df(sin, pi/4))
print('df(cos, pi/4)=', df(cos, pi/3))
print('df(x^2, 3)=', df(lambda x:x**2, 3))
