## 練習 -- publish

1. Add files
2. test
3. publish

```
$ mocha
module.js:545
    throw err;
    ^

Error: Cannot find module 'chai'
    at Function.Module._resolveFilename (module.js:543:15)
    at Function.Module._load (module.js:470:25)
    at Module.require (module.js:593:17)
    at require (internal/module.js:11:18)
    at Object.<anonymous> (D:\GoogleDrive\course\se107a\example\02-npm\02-addfile\test\concatTest.js:1:78)
    at Module._compile (module.js:649:30)
    at Object.Module._extensions..js (module.js:660:10)
    at Module.load (module.js:561:32)
    at tryModuleLoad (module.js:501:12)
    at Function.Module._load (module.js:493:3)
    at Module.require (module.js:593:17)
    at require (internal/module.js:11:18)
    at C:\Users\user\AppData\Roaming\npm\node_modules\mocha\lib\mocha.js:231:27
    at Array.forEach (<anonymous>)
    at Mocha.loadFiles (C:\Users\user\AppData\Roaming\npm\node_modules\mocha\lib\mocha.js:228:14)
    at Mocha.run (C:\Users\user\AppData\Roaming\npm\node_modules\mocha\lib\mocha.js:536:10)
    at Object.<anonymous> (C:\Users\user\AppData\Roaming\npm\node_modules\mocha\bin\_mocha:582:18)
    at Module._compile (module.js:649:30)
    at Object.Module._extensions..js (module.js:660:10)
    at Module.load (module.js:561:32)
    at tryModuleLoad (module.js:501:12)
    at Function.Module._load (module.js:493:3)
    at Function.Module.runMain (module.js:690:10)
    at startup (bootstrap_node.js:194:16)
    at bootstrap_node.js:666:3
$ npm i chai --save
npm notice created a lockfile as package-lock.json. You should commit this file.
npm WARN ccclodash@0.0.2 No repository field.

+ chai@4.1.2
added 7 packages in 7.663s
$ mocha

  ccclodash
    chunk
      √ _.chunk(['a', 'b', 'c', 'd'], 2) equalTo [ [ 'a', 'b' ], [ 'c', 'd' ] ]
      √ _.chunk(['a', 'b', 'c', 'd'], 3) equalTo [ [ 'a', 'b', 'c' ], [ 'd' ] ]
      √ _.chunk(['a', 'b', 'c', 'd'], 3) notEqualTo [ [ 'a', 'b'], ['c' , 'd' ] ]

  ccclodash
    compact
      √ _.compact([0, 1, false, 2, '', 3]) equalTo [ 1, 2, 3 ]

  ccclodash
    concat
      √ _.concat(array, 2, [3], [[4]]) equalTo [1, 2, [3], [[4]]]
      √ _.concat(array, 2, [3], [[4]]) equalTo [ 1, 2, 3 ]


  6 passing (68ms)
```

