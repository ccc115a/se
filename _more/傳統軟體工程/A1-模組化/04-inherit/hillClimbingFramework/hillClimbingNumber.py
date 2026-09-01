from hillClimbing import hillClimbing # 引入爬山演算法類別
from solutionNumber import SolutionNumber # 引入平方根解答類別

# 執行爬山演算法 (從「解答=0.0」開始尋找, 最多十萬代、失敗一千次就跳出。
hillClimbing(SolutionNumber(0.0), 100000, 1000)
