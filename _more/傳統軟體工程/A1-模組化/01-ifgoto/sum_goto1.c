#include <stdio.h>

int sum(int n) {
    int s=0, i=1;
_begin:
    // while (i <= n) {
    if (i>n) goto _end;
    s+=i;
    i++;
    goto _begin;
_end:
    return s;
}

int main() {
    printf("sum(10)=%d\n", sum(10));
    printf("sum(100)=%d\n", sum(100));
}
