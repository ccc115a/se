

from hillClimbing import hillClimbing # 引入爬山演算法類別
from solutionLp import SolutionLp # 引入解答類別

# 執行爬山演算法 (最多十萬代、失敗一千次就跳出)。
hillClimbing(SolutionLp([0,0,0]), 10000000, 10000)
# 最後沒找到最佳解，似乎不只一個山峰