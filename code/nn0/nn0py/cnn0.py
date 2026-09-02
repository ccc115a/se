# cnn.py
import math
import random
from nn0 import Value

class Conv2d:
    def __init__(self, in_channels, out_channels, kernel_size):
        self.in_c = in_channels
        self.out_c = out_channels
        self.ks = kernel_size
        
        # 使用 He Uniform 初始化權重（適合 ReLU）
        fan_in = in_channels * kernel_size * kernel_size
        bound = math.sqrt(6.0 / fan_in)
        
        # 權重維度: [out_channels][in_channels][kernel_size][kernel_size]
        self.w = [[[[Value(random.uniform(-bound, bound)) for _ in range(kernel_size)]
                    for _ in range(kernel_size)]
                   for _ in range(in_channels)]
                  for _ in range(out_channels)]
        # 偏置: [out_channels]
        self.b = [Value(0.0) for _ in range(out_channels)]

    def __call__(self, x):
        """x 形狀: (C, H, W) 嵌套列表"""
        C, H, W = len(x), len(x[0]), len(x[0][0])
        out_H = H - self.ks + 1
        out_W = W - self.ks + 1

        out =[]
        for oc in range(self.out_c):
            out_c_map = []
            for i in range(out_H):
                row =[]
                for j in range(out_W):
                    # 計算卷積: 乘加累計
                    val = self.b[oc]
                    for ic in range(self.in_c):
                        for ki in range(self.ks):
                            for kj in range(self.ks):
                                val = val + x[ic][i+ki][j+kj] * self.w[oc][ic][ki][kj]
                    row.append(val)
                out_c_map.append(row)
            out.append(out_c_map)
        return out

    def parameters(self):
        params = self.b.copy()
        for oc in self.w:
            for ic in oc:
                for row in ic:
                    params.extend(row)
        return params

class MaxPool2d:
    def __init__(self, kernel_size=2, stride=2):
        self.ks = kernel_size
        self.stride = stride

    def __call__(self, x):
        """x 形狀: (C, H, W) 嵌套列表"""
        C, H, W = len(x), len(x[0]), len(x[0][0])
        out_H = H // self.stride
        out_W = W // self.stride

        out =[]
        for c in range(C):
            out_c_map =[]
            for i in range(out_H):
                row = []
                for j in range(out_W):
                    pool_vals =[]
                    for ki in range(self.ks):
                        for kj in range(self.ks):
                            pool_vals.append(x[c][i*self.stride + ki][j*self.stride + kj])
                    # 選擇數值最大的 Value 節點。這會自動將梯度導向該節點，完美實現 Max Pooling 自動微分！
                    max_v = max(pool_vals, key=lambda v: v.data)
                    row.append(max_v)
                out_c_map.append(row)
            out.append(out_c_map)
        return out

    def parameters(self):
        return[]

class Linear:
    def __init__(self, in_features, out_features):
        self.in_f = in_features
        self.out_f = out_features
        bound = math.sqrt(6.0 / in_features)
        self.w = [[Value(random.uniform(-bound, bound)) for _ in range(in_features)] for _ in range(out_features)]
        self.b = [Value(0.0) for _ in range(out_features)]

    def __call__(self, x):
        """x 是 1D 列表"""
        out =[]
        for i in range(self.out_f):
            val = self.b[i]
            for j in range(self.in_f):
                val = val + x[j] * self.w[i][j]
            out.append(val)
        return out

    def parameters(self):
        params = self.b.copy()
        for row in self.w:
            params.extend(row)
        return params

class CNN:
    def __init__(self):
        # 假設輸入影像經過了降採樣，尺寸為 1x14x14
        # 卷積後: 4x12x12
        self.conv1 = Conv2d(in_channels=1, out_channels=4, kernel_size=3)
        # 池化後: 4x6x6
        self.pool1 = MaxPool2d(kernel_size=2, stride=2)
        # 全連接映射到 10 個類別 (0~9)
        self.fc1 = Linear(in_features=4 * 6 * 6, out_features=10)

    def __call__(self, x):
        x = self.conv1(x)
        # 應用 ReLU 激活函數
        x = [[[v.relu() for v in row] for row in c_map] for c_map in x]
        x = self.pool1(x)
        
        # Flatten (展平)
        x_flat =[]
        for c_map in x:
            for row in c_map:
                x_flat.extend(row)
                
        out = self.fc1(x_flat)
        return out

    def parameters(self):
        return self.conv1.parameters() + self.fc1.parameters()