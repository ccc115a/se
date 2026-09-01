import ai6

def f(p):
	[x,y] = p
	return x*x + y*y

p = [1.0, 3.0]
ai6.gradient_descendent(f, p)
