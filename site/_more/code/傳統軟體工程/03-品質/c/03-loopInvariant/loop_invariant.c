int fsum(int n, int x) {
  int s = 0;
  for (int i=0; i<n; i++) {
    s += x*x + i*i;
  }
  return s;
}
