"""
A X = B ，求 X 是多少？

範例：題目來源: http://mail.im.tku.edu.tw/~idliaw/LinTup/99ie/99IEntu.pdf

4a+3b+6c=1
1a+1b+2c=2
2a+1b+3c=-1
"""

from random import random, randint
import numpy as np
from numpy import linalg as LA
from solution import Solution

A = np.array([[4,3,6],[1,1,2],[2,1,3]])
B = np.array([[1,2,-1]]).transpose()

class SolutionEquation(Solution):
    def neighbor(self):    #  多變數解答的鄰居函數。
        nx = self.v.copy()              #  複製目前解的矩陣
        rows = nx.shape[0]
        #  修改了這裡：最多改變 n 個維度(只是某些 n 維的例子可以，無法確定一定可以，除非能證明能量函數只有一個低點)
        for _ in range(rows):         #  原本只改一維，會找不到！
            i = randint(0, rows-1) #  隨機選取一個變數
            if (random() > 0.5):                    #  擲骰子決定要往左或往右移
                nx[i][0] += self.step * random()  #  原本是 nx.m[i][0] += self.step 
            else:
                nx[i][0] -= self.step * random()  #  原本是 nx.m[i][0] -= self.step 

        return SolutionEquation(nx)                    #  傳回新建的鄰居解答。

    def energy(self):      #  能量函數:計算 ||AX-B||，也就是 ||Y-B||
        X = self.v
        Y = A.dot(X)
        return LA.norm(Y-B, 2)

    def str(self):    #  將解答轉為字串的函數，以供列印用。
        return "energy({:s})={:f}".format(str(self.v.transpose()), self.energy())

    @classmethod
    def zero(cls):
        return SolutionEquation(np.zeros((3,1)))

