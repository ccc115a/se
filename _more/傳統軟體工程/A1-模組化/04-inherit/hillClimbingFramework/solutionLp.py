from solution import Solution
from random import random, randint
'''
var input = {
	type: "maximize",
	objective : "x1 + 2x2 - x3",
	constraints : [
		"2x1 + x2 + x3 <= 14",
		"4x1 + 2x2 + 3x3 <= 28",
		"2x1 + 5x2 + 5x3 <= 30"
	]
};

$ deno run simplex.js
Output { result: { x1: 5, x2: 4, x3: 0, slack1: 0, slack2: 0, slack3: 0, z: 13 } 
}

$ python hillClimbingLp.py
...
solution:  height([2.474300927511427, 5.0102214808619525, 8.916215196012818e-06])=12.494735
# 最後沒找到最佳解，似乎不只一個山峰
'''
class SolutionLp(Solution):
    def neighbor(self):           #  多變數解答的鄰居函數。
        nv = self.v.copy()        #  nv=v.clone()=目前解答的複製品
        for i in range(len(nv)):
            nv[i] += (random()-0.5)*self.step
        return SolutionLp(nv)  #  傳回新建的鄰居解答。

    def height(self): 
        x1, x2, x3 =self.v
        r1 = 2*x1+x2+x3-14
        r2 = 4*x1+2*x2+3*x3-28
        r3 = 2*x1+5*x2+5*x3-30
        p1 = r1 if r1>0 else 0
        p2 = r2 if r2>0 else 0
        p3 = r3 if r3>0 else 0
        e1 = -x1 if x1<0 else 0
        e2 = -x2 if x2<0 else 0
        e3 = -x3 if x3<0 else 0
        return (x1+2*x2-x3)-1000*(p1+p2+p3+e1+e2+e3)

    def str(self):    #  將解答轉為字串的函數，以供列印用。
        return "height({:s})={:f}".format(str(self.v), self.height())


