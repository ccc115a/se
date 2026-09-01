var fs = require("fs");
var c  = console;
var file = process.argv[2];

var dtable = {
  ""   :0b000,
  "M"  :0b001,
  "D"  :0b010,
  "MD" :0b011,
  "A"  :0b100,
  "AM" :0b101,
  "AD" :0b110,
  "AMD":0b111
}

var jtable = {
  ""   :0b000,
  "JGT":0b001,
  "JEQ":0b010,
  "JGE":0b011,
  "JLT":0b100,
  "JNE":0b101,
  "JLE":0b110,
  "JMP":0b111
}

var ctable = {
  "0"   :0b0101010,
  "1"   :0b0111111,
  "-1"  :0b0111010,
  "D"   :0b0001100,
  "A"   :0b0110000, 
  "M"   :0b1110000,
  "!D"  :0b0001101,
  "!A"  :0b0110001, 
  "!M"  :0b1110001,
  "-D"  :0b0001111,
  "-A"  :0b0110011,
  "-M"  :0b1110011,
  "D+1" :0b0011111,
  "A+1" :0b0110111,
  "M+1" :0b1110111,
  "D-1" :0b0001110,
  "A-1" :0b0110010,
  "M-1" :0b1110010,
  "D+A" :0b0000010,
  "D+M" :0b1000010,
  "D-A" :0b0010011,
  "D-M" :0b1010011,
  "A-D" :0b0000111,
  "M-D" :0b1000111,
  "D&A" :0b0000000,
  "D&M" :0b1000000,
  "D|A" :0b0010101,
  "D|M" :0b1010101
}

var symTable = {
  "R0"  :0,
  "R1"  :1,
  "R2"  :2,
  "R3"  :3,
  "R4"  :4,
  "R5"  :5,
  "R6"  :6,
  "R7"  :7,
  "R8"  :8,
  "R9"  :9,
  "R10" :10,
  "R11" :11,
  "R12" :12,
  "R13" :13,
  "R14" :14,
  "R15" :15,
  "SP"  :0,
  "LCL" :1,
  "ARG" :2,
  "THIS":3, 
  "THAT":4,
  "KBD" :24576,
  "SCREEN":16384
};

var symTop = 16;

function addSymbol(symbol) {
  symTable[symbol] = symTop;
  symTop ++;
}

/**
 * 組譯: hack 組合語言組譯器，將組合語言轉換成機器碼
 * @param {String} asmFile
 * @param {String} objFile
 */
function assemble(asmFile, objFile) {
  var asmText = fs.readFileSync(asmFile, "utf8"); // 讀取檔案到 text 字串中
  var lines   = asmText.split(/\r?\n/); // 將組合語言分割成一行一行
  c.log(JSON.stringify(lines, null, 2));
  //  第一階段：計算所有符號的位址，建立符號表。
  pass1(lines);
  // 第二階段：根據指令表與符號表，將組合語言轉換成機器碼。
  pass2(lines, objFile);
} 

/**
 * 第一階段：計算所有符號的位址，建立符號表。
 * @param {Array} lines 一行一行的組合語言
 * @returns {Object} 符號表，記錄了符號的位址
 */
function pass1(lines) {
  c.log("============== pass1 ================");
  var address = 0;
  for (var i=0; i<lines.length; i++) {
    var p = parse(lines[i], i); // 剖析該行
    if (p===null) continue;
    if (p.type === "S") { // 若該行有符號，則記錄符號位址
      c.log(" symbol: %s %s", p.symbol, intToStr(address, 4, 10));
      symTable[p.symbol] = address;
      continue;
    } else {
      c.log(" p: %j", p);
    }
    c.log("%s:%s %s", intToStr(i+1, 3, 10), intToStr(address, 4, 10),  lines[i]);
    address++; // 計算下一行位址
  }
  return symTable
}

/**
 * 第二階段：根據指令表與符號表，將組合語言轉換成機器碼，寫入到目的檔中。
 * @param {Array} lines 一行一行的組合語言
 * @param {String} objFile 目的檔
 */
function pass2(lines, objFile) {
  c.log("============== pass2 ================");
  var ws = fs.createWriteStream(objFile);
  ws.once('open', function(fd) {
    var address = 0;
    for (var i=0; i<lines.length; i++) {
      var p = parse(lines[i], i); // 剖析該行
      if (p===null || p.type === "S") continue;
      var code = toCode(p); // 將該行《轉為機器碼》
      c.log("%s:%s %s", intToStr(i+1, 3, 10), intToStr(code, 16, 2),  lines[i]);
      ws.write(intToStr(code, 16, 2)+"\n");
      address++; // 計算下一行位址
    }
    ws.end();
  });
}

/**
 * 剖析: 將一行組合語言拆成個別欄位
 * @param {*} line 一行一行的組合語言
 * @param {*} i 目前是第 i 行 (有錯時可提示錯誤訊息)
 * @returns {Object} 剖析後的物件 (欄位組合)
 */
function parse(line, i) {
  line.match(/^([^\/]*)(\/.*)?$/);
  line = RegExp.$1.trim();
  if (line.length===0)
    return null;
  if (line.startsWith("@")) {
    // A 指令 : {@(symbol || number)}
    return { type:"A", arg:line.substring(1).trim() }
  } else if (line.match(/^\(([^\)]+)\)$/)) {
    // 符號行 : (symbol)
    return { type:"S", symbol:RegExp.$1 }
  } else if (line.match(/^((([AMD]*)=)?([AMD01\+\-\&\|\!]*))(;(\w*))?$/)) {
    // C 指令 : d = c; j
    return { type:"C", c:RegExp.$4, d:RegExp.$3, j:RegExp.$6 }
  } else {
    throw "Error: line "+(i+1);
  }
}

/**
 * 轉為機器碼
 * @param {Object} p 剖析後的組合語言結構
 * @returns {Integer} 二進位機器碼
 */
function toCode(p) {
  var address; 
  if (p.type === "A") {
    if (p.arg.match(/^\d+$/)) {
      address = parseInt(p.arg);
    } else {
      address = symTable[p.arg];
      if (typeof address === 'undefined') {
        address = symTop;
        addSymbol(p.arg, address);
        // throw new Error(p.arg + '===undefined')
      }
    }
    return address; 
  } else { // if (p.type === "C")
    var dx = dtable[p.d];
    var cx = ctable[p.c];
    var jx = jtable[p.j];
    return 0b111<<13|cx<<6|dx<<3|jx;
  }
}

/**
 * 將整數轉換成 n 進位
 * @param {*} num 整數
 * @param {*} size 輸出的二進位長度
 * @param {*} radix radix = n 進位 
 */
function intToStr(num, size, radix) {
  //  c.log(" num="+num);
  var s = num.toString(radix)+"";
  while (s.length < size) s = "0" + s;
  return s;
}
  
if (!module.parent) assemble(file+'.asm', file+'.hack');
