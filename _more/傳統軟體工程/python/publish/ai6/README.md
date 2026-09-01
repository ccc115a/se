# ai6 -- Artificial Intelligence Code Examples

## Install

```
$ pip install ai6
```

## Example

```py
import ai6

def f(p):
	[x,y] = p
	return x*x + y*y

p = [1.0, 3.0]
ai6.gradient_descendent(f, p)
```
