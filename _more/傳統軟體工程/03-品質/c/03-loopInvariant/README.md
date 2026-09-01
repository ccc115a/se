# Loop Invariant -- 迴圈不變量

```
PS D:\ccc\sp\code\c\08-compiler2\optimize\02-loopInvariant> gcc -O0 -S loop_invariant.c -o loop_invariant_O0.s
PS D:\ccc\sp\code\c\08-compiler2\optimize\02-loopInvariant> gcc -O3 -S loop_invariant.c -o loop_invariant_O3.s
PS D:\ccc\sp\code\c\08-compiler2\optimize\02-loopInvariant> gcc -O3 -S mystrcpy1.c -o mystrcpy1_O3.s
PS D:\ccc\sp\code\c\08-compiler2\optimize\02-loopInvariant> gcc -O0 -S mystrcpy1.c -o mystrcpy1_O0.s
```