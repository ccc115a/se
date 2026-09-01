#include <stdio.h>

int main() {
    int n=10;
    int s=0, i=1;
_begin:
    if (i>n) goto _end;
    s+=i;
    i++;
    goto _begin;
_end:

    printf("sum(10)=%d\n", s);

    n = 100;
    s = 0; i=1;
_begin2:
    if (i>n) goto _end2;
    s+=i;
    i++;
    goto _begin2;
_end2:
    printf("sum(100)=%d\n", s);
}
