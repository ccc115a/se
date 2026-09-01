# bits struct 

## 使用 SHORT 成功

```
PS D:\ccc\sp\code\c\08-compiler2\optimize\05-struBits> gcc struBits.c -o  struBits
PS D:\ccc\sp\code\c\08-compiler2\optimize\05-struBits> ./struBits
sizeof(iA)=2
sizeof(Instr)=2
sizeof(iC)=2
PS D:\ccc\sp\code\c\08-compiler2\optimize\05-struBits> gcc -S -fpack-struct struBits.c -o  struBitsPack.s
```

## 使用 CHAR ，失敗

```
PS D:\ccc\sp\code\c\08-compiler2\optimize\05-struBits> gcc -S struBits.c -o struBits.s
PS D:\ccc\sp\code\c\08-compiler2\optimize\05-struBits> gcc -fverbose-asm -S struBits.c -o struBits.s
 struBits.c -o struBits.s
PS D:\ccc\sp\code\c\08-compiler2\optimize\05-struBits> ./struBits
sizeof(iA)=3
sizeof(Instr)=3
sizeof(iC)=3
ruBits
 struBits.c -o struBits.s
PS D:\ccc\sp\code\c\08-compiler2\optimize\05-struBits> ./struBits
sizeof(iA)=3
sizeof(Instr)=3
sizeof(iC)=3
0 -S struBits.c -o struBits.s
PS D:\ccc\sp\code\c\08-compiler2\optimize\05-struBits> gcc -O0 struBits.c -o struBits
PS D:\ccc\sp\code\c\08-compiler2\optimize\05-struBits> ./struBits
sizeof(iA)=3
PS D:\ccc\sp\code\c\08-compiler2\optimize\05-struBits> gcc -O3 struBits.c -o struBits
PS D:\ccc\sp\code\c\08-compiler2\optimize\05-struBits> ./struBits
sizeof(iA)=3
sizeof(Instr)=3
sizeof(iC)=3
PS D:\ccc\sp\code\c\08-compiler2\optimize\05-struBits> gcc -fpack-struct struBits.c -o struBitsPack
PS D:\ccc\sp\code\c\08-compiler2\optimize\05-struBits> ./struBitPack       
./struBitPack : 無法辨識 './struBitPack' 詞彙是否為 Cmdlet、函數、指令檔或
正確，然後再試一次。
位於 線路:1 字元:1
+ ./struBitPack
+ ~~~~~~~~~~~~~
   CommandNotFoundException
    + FullyQualifiedErrorId : CommandNotFoundException
 
PS D:\ccc\sp\code\c\08-compiler2\optimize\05-struBits> ./struBitsPack      
sizeof(iA)=3
sizeof(iC)=3
PS D:\ccc\sp\code\c\08-compiler2\optimize\05-struBits> gcc -Os -fpack-struct struBits.c -o  struBitsPack
PS D:\ccc\sp\code\c\08-compiler2\optimize\05-struBits> ./struBitsPack      
sizeof(iA)=3
sizeof(Instr)=3
sizeof(iC)=3
PS D:\ccc\sp\code\c\08-compiler2\optimize\05-struBits> gcc -Os -fpack-struct struBits.c -o  struBitsPack
PS D:\ccc\sp\code\c\08-compiler2\optimize\05-struBits> ./struBitsPack      
sizeof(iA)=3
sizeof(Instr)=3
sizeof(iC)=3
```