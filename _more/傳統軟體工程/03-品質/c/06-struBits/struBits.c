#include <stdio.h>
#include <stdint.h>

typedef struct _Instr {
  unsigned short isC:1, :2, a:1, c:6, d:3, j:3;
} Instr;

int main() {
  Instr iA; // = (Instr) 0x000F;
  Instr iC; //  = (Instr) 0x8010;
  printf("sizeof(iA)=%d\n", sizeof(iA));
  printf("sizeof(Instr)=%d\n", sizeof(Instr));
  printf("sizeof(iC)=%d\n", sizeof(iC));
  iC.a = 1;
  iC.c = 0x03;
}
