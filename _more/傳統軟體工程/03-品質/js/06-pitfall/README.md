# 練習 Pitfall -- 語言的陷阱

1. 請找出 strict.js 的程式 bug，該程式應該要輸出 0, 1, 2, 4, 5, 6, 7, 8, 9 (沒有 3)

## JavaScript

* https://www.artificialworlds.net/presentations/javascript-wtfs/javascript-wtfs.html (讚！)
* https://stackoverflow.com/questions/2749952/what-are-the-top-javascript-pitfalls
* https://secure.phabricator.com/book/phabflavor/article/javascript_pitfalls/
* https://www.codementor.io/thinker3197/avoid-common-pitfalls-in-javascript-u0hzz2nfw

```js
$ node
> 0.1+0.2
0.30000000000000004
> (0.1+0.2)===0.3
false
> 3 == "3"
true
> '' == 0
true
> 0 == ''
true
> 1 == ''
false
> null == undefined
true
> null === undefined
false
> '  \r\n ' == 0
true
> {} == {}
false
> {} === {}
false
> function f() {
... return
... {
..... a:3
..... }
... }
undefined
> f()
undefined
> typeof NaN
'number'
> typeof []
'object'
> typeof null
'object'
> typeof undefined
'undefined'
> parseInt('2.57')
2
> parseInt('2 is a prime number')
2
> parseInt('015')
15
> parseInt('015', 8)
13
> for( var i in [ 21, 22, 23 ] ) { console.log( i ); };
0
1
2
undefined
> var a = [ 30, 31, 32]
undefined
> a.name = 3
3
> a
[ 30, 31, 32, name: 3 ]
> a.length = 5
5
> a
[ 30, 31, 32, <2 empty items>, name: 3 ]
> var a = [ 32, 14, 11, 112, 17 ]
undefined
> a.sort()
[ 11, 112, 14, 17, 32 ]
> typeof null
'object'
> typeof undefined2
'undefined'
> typeof []
'object'
> typeof {}
'object'
> typeof "abc"
'string'
> typeof true
'boolean'
> typeof function(){}
'function'
> typeof class {}
'function'
> NaN === Nan
ReferenceError: Nan is not defined
> NaN === NaN
false
> NaN !== NaN
true
> isNaN(NaN)
true
> isNaN('abc')
true
> isNaN('0')
false
> var i=1
undefined
> if (i=2) console.log('i!=1')
i!=1
```


## C

* [ptt C 語言新手十誡](http://dangerlover9403.pixnet.net/blog/post/193048854-%5B%E5%88%86%E4%BA%AB%5D-ptt-c-%E8%AA%9E%E8%A8%80%E6%96%B0%E6%89%8B%E5%8D%81%E8%AA%A1) (讚！)
    * https://www.ptt.cc/bbs/C_and_CPP/M.1268491365.A.EF7.html
* http://www.literateprogramming.com/ctraps.pdf



## Python

* https://www.toptal.com/python/top-10-mistakes-that-python-programmers-make
* https://stackoverflow.com/questions/1011431/common-pitfalls-in-python

# Go

* http://devs.cloudimmunity.com/gotchas-and-common-mistakes-in-go-golang/

## 參考

* https://eloquentjavascript.net/08_error.html
* [What the f*ck JavaScript?](https://github.com/denysdovhan/wtfjs/blob/master/README-zh-cn.md)
* [10 COMMON JAVASCRIPT BUGS AND HOW TO AVOID THEM](https://www.dummies.com/web-design-development/javascript/10-common-javascript-bugs-and-how-to-avoid-them/)