// 請為本程式加上 try catch 的錯誤處理！

const fs = require('fs')

var text = fs.readFileSync(process.argv[2], 'utf8')

console.log('file=', text)
