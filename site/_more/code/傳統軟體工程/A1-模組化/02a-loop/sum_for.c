#include <stdio.h>

int main() {
    int n=10, s, i;

_sum:
    s=0;
    for (i=1; i<=n;i++)
        s+=i;

    if (n == 100) goto _printSum100;

    printf("sum(10)=%d\n", s);

    n = 100;
    goto _sum;

_printSum100:
    printf("sum(100)=%d\n", s);
}
