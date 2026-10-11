#include <stdio.h>

/* A loop with work that does not need to be redone every time. */
int main() {
    int sum = 0;
    for (int i = 0; i < 10; i++) {
        int step = 2 + 3;         /* same value on every pass */
        sum += step * 1;
    }
    printf("%d\n", sum);
    return 0;
}
