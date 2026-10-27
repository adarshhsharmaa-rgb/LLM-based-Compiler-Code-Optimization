#include <stdio.h>

/* The rules clean up the loop body; the LLM can replace the whole loop. */
int main() {
    int price = 20 + 5;
    int unused = price * 3;       /* never printed: dead code */
    int total = 0;

    for (int day = 1; day <= 7; day++) {
        int tax = 2 * 1;          /* same value on every pass */
        total += price + tax;
    }

    printf("%d\n", total);
    return 0;
}
