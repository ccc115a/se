import math
import random

def P(e, enew, T): # 模擬退火法的機率函數
    if (enew < e):
        return 1
    else:
        return math.exp((e-enew)/T)

def annealing(s, maxGens) : # 模擬退火法的主要函數
    sbest = s                              # sbest:到目前為止的最佳解
    ebest = s.energy()                     # ebest:到目前為止的最低能量
    T = 100                                # 從 100 度開始降溫
    for gens in range(maxGens):            # 迴圈，最多作 maxGens 這麼多代。
        snew = s.neighbor()                # 取得鄰居解
        e    = s.energy()                  # e    : 目前解的能量
        enew = snew.energy()               # enew : 鄰居解的能量
        T  = T * 0.995                     # 每次降低一些溫度
        if P(e, enew, T)>random.random():  # 根據溫度與能量差擲骰子，若通過
            s = snew                       # 則移動到新的鄰居解
            print("{} T={:.5f} {}".format(gens, T, s.str())) # 印出觀察

        if enew < ebest:                 # 如果新解的能量比最佳解好，則更新最佳解。
            sbest = snew
            ebest = enew
    
    print("solution: {}", sbest.str())     # 印出最佳解
    return sbest                           # 傳回最佳解
