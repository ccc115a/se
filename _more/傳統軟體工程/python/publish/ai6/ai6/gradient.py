import numpy as np
from numpy.linalg import norm

# 函數 f 對變數 k 的偏微分: df / dk
def df(f, p, k, step=0.01):
	p1 = p.copy()
	p1[k] = p[k]+step
	return (f(p1) - f(p)) / step

# 函數 f 在點 p 上的梯度
def grad(f, p, step=0.01):
	gp = p.copy()
	for k in range(len(p)):
		gp[k] = df(f, p, k, step)
	return gp

# 使用梯度下降法尋找函數最低點
def gradient_descendent(f, p0, step=0.001):
	p = p0.copy()
	while (True):
		gp = grad(f, p) # 計算梯度 gp
		glen = norm(gp) # norm = 梯度的長度 (步伐大小)
		print('p=', p, 'f(p)=', f(p), 'glen=', glen)
		if glen < 0.00001:  # 如果步伐已經很小了，那麼就停止吧！
			break
		# gstep = np.mul(gp, -1 * step) # gstep = 逆梯度方向的一小步
		gstep = np.multiply(gp, -1*step)
		p +=  gstep # 向 gstep 方向走一小步
	return p # 傳回最低點！
