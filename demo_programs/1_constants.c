#include <stdio.h>

/* Everything here can be worked out at compile time. */
int main() {
    int width = 4 + 6;
    int height = width * 2;
    int area = width * height;
    int unused = area * 100;      /* never printed: dead code */
    int result = area + 0;        /* x + 0 is just x */
    printf("%d\n", result * 1);
    return 0;
}
