# 軟件架構

* [The Architecture of Open Source Applications](http://aosabook.org/en/index.html)
    * 中文版: [开源软件架构](https://www.ituring.com.cn/book/1143)

請畫出你的系統架構圖，並說明這樣配置的原因。

例如：結合 MessageQueue (RabbitMQ) 作為訊息發派系統，然後用 Redis 作為緩存系統 (以加快速度)，加上 MongoDB 資料庫。

## 資料存儲

請選擇你所需要的存儲搭配，實作出 iChat 的資料存儲架構 (例如 Redis + MongoDB) ...

並說明你採用這種搭配的理由。

然後設計出資料庫的結構 (包含表格、欄位、索引建、快取內容 ....)。

## 該如何選資料庫

* 強調一致姓 : SQL ...
* 強調彈性 : MongoDB, ...
* 強調速度 : Hadoop ....
* 全文檢索 : ElasticSearch ...

## node.js 的套件
* http://docs.sequelizejs.com/
  * [访问MySQL](https://www.liaoxuefeng.com/wiki/001434446689867b27157e896e74d51a89c25cc8b43bdb3000/001471955049232be7492e76f514d45a2180e2c224eb7a6000)