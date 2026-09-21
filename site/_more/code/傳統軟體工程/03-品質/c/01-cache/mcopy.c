#include <stdio.h>
#include <time.h>

#define M 10000
#define N 20000
int a[M][N], b[M][N];

void copy_ij() {
  for (int i=0; i<M; i++) {
    for (int j=0; j<N; j++) {
      b[i][j] = a[i][j];
    }
  }
}

void copy_ji() {
  for (int j=0; j<N; j++) {
    for (int i=0; i<M; i++) {
      b[i][j] = a[i][j];
    }
  }
}

void run(void (*copy)(), char *fname) {
  printf("========= %s ============\n", fname);
  time_t start, stop;
  // init();
  start = time(NULL);
  printf("start=%d\n", start);
  copy();
  stop  = time(NULL);
  printf("stop =%d\n", stop);
  printf("diff =%d\n", stop-start);
}

int main() {
  run(copy_ij, "copy_ij");
  run(copy_ji, "copy_ji");
}