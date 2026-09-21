#include <stdio.h>

int R = 0;
void f0() { R = 0; }
void f1() { R = 1; }
void f2() { R = 2; }
void f3() { R = 3; }
void f4() { R = 4; }

typedef void (*F)();

#define TSIZE 5

F table[TSIZE]={f0,f1,f2,f3,f4};

int main() {
    for (int i=0; i<TSIZE; i++) {
        switch (i) {
          case 0: f0(); break;
          case 1: f1(); break;
          case 2: f2(); break;
          case 3: f3(); break;
          case 4: f4(); break;
        }
        printf("R=%d\n", R);
    }
}
