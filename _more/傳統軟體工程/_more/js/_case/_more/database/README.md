# database

## 關連式資料庫

* [資料庫正規化(PDF)](http://cc.cust.edu.tw/~ccchen/doc/db_04.pdf)
* [Wikipedia:資料庫正規化](https://zh.wikipedia.org/wiki/%E6%95%B0%E6%8D%AE%E5%BA%93%E8%A7%84%E8%8C%83%E5%8C%96)

## ER-diagram

* [Chapter 2: Entity-Relationship Model(PDF)](https://ssyu.im.ncnu.edu.tw/course/CSDB/chap2.pdf)
* [Entity Relationship Diagram – ER Diagram in DBMS](https://beginnersbook.com/2015/04/e-r-model-in-dbms/)

## 範例

```
id name   age
--------------
1  ccc    50
2  snoopy 3
```

```json
{
  name:"ccc",
  age: 50,
  friends: [ "snoopy", "garfield"]
}
```

```
id name   age    friends
--------------------------
1  ccc    50     ["snoopy", "garfield"]
2  snoopy 3
```

```
const posts = [
  {id:0, title:'aaa', body:'aaaaa'},
  {id:1, title:'bbb', body:'bbbbb'},
  {id:2, title:'ccc', body:'ccccc'},
  {id:3, title:'ddd', body:'ddddd'},
];
```



people

id name   age
--------------
1  ccc      50
2  snoopy   3
3  garfield 7
...

friends

id  fid
--------------
1   2
1   3

{
  filename: 
  url: 
  page: 
}

id   url                page
-------------------------------
1    http://yahoo.com   Yahoo ....
