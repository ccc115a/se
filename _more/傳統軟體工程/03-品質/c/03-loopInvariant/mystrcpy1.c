#include <string.h>

int mystrcpy1(char *source, char *target) {
  int len = strlen(source);
  for (int i=0; i<len; i++) {
    target[i] = source[i];
  }
}

int mystrcpy2(char *source, char *target) {
  for (int i=0; i<strlen(source); i++) {
    target[i] = source[i];
  }
}
