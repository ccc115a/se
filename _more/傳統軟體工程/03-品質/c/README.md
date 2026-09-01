# 軟硬體的效能

1. 快取原則: 
    * 降低慢速裝置的存取次數或數量 (ex: 二元樹 => BTree)，盡量以快速裝置作為快取。
    * Amdahl's Law -- https://en.wikipedia.org/wiki/Amdahl%27s_law
    * https://chi_gitbook.gitbooks.io/personal-note/content/amdahls_law.html
2. 平行算法: mutex、 semaphore，
    * [拜占庭將軍問題](https://zh.wikipedia.org/wiki/%E6%8B%9C%E5%8D%A0%E5%BA%AD%E5%B0%86%E5%86%9B%E9%97%AE%E9%A2%98)
    * [哲學家就餐問題](https://zh.wikipedia.org/zh-hant/%E5%93%B2%E5%AD%A6%E5%AE%B6%E5%B0%B1%E9%A4%90%E9%97%AE%E9%A2%98)
    * [生產者消費者問題](https://zh.wikipedia.org/zh-hant/%E7%94%9F%E4%BA%A7%E8%80%85%E6%B6%88%E8%B4%B9%E8%80%85%E9%97%AE%E9%A2%98)
3. 採用好的演算法
    * 排序：泡沫排序 => 合併俳序 => 快速排序。
    * 搜尋：暴力搜尋 => 二分搜尋
    * 最短路徑：廣度優先搜尋 (最佳優先搜尋) => Dijkstra 算法
4. 恰當的資料結構，例如：
    * 二元樹 => 紅黑樹 : 高度平衡，複雜度永遠是 O(log n)
    * 排序 => Heap : 當順序不重要，但需要反覆取最小 (或最大) 元素的時候。
    * 二元樹 => 雜湊表 : 當碰撞率很低，可以浪費一些空間以換取速度時。
