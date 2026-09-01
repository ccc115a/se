# ccclodash

Reimplement some function of lodash, just a practice

## Install

```
$ npm i ccclodash
```

## Example

File : ex1.js

```js
const _ = require('../ccclodash')

console.log("_.chunk(['a', 'b', 'c', 'd'], 2)=", _.chunk(['a', 'b', 'c', 'd'], 2))
console.log("_.chunk(['a', 'b', 'c', 'd'], 3)=", _.chunk(['a', 'b', 'c', 'd'], 3))

```

Run

```
$ node ex1.js
_.chunk(['a', 'b', 'c', 'd'], 2)= [ [ 'a', 'b' ], [ 'c', 'd' ] ]
_.chunk(['a', 'b', 'c', 'd'], 3)= [ [ 'a', 'b', 'c' ], [ 'd' ] ]
```

## Test

```
$ mocha

  cccLodash

      √ _.chunk(['a', 'b', 'c', 'd'], 2) equalTo [ [ 'a', 'b' ], [ 'c', 'd' ] ]
      √ _.chunk(['a', 'b', 'c', 'd'], 3) equalTo [ [ 'a', 'b', 'c' ], [ 'd' ] ]
      √ _.chunk(['a', 'b', 'c', 'd'], 3) notEqualTo [ [ 'a', 'b'], ['c' , 'd' ] ]


  3 passing (35ms)

```