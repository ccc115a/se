#include <stdio.h>

int sum(int n) {
    int s=0, i=1;
    while (i <= n) {
        s+=i;
        i++;
    }
    return s;
}

int main() {
    printf("sum(10)=%d\n", sum(10));
    printf("sum(100)=%d\n", sum(100));
}
