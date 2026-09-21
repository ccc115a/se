int x = 3;

void test() {
  if (x < 5) goto L1;
  x = 100;
L1:
  return;
}