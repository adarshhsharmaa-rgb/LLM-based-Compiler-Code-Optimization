#include <stdio.h>

/* The value of n comes from the user, so it cannot be folded away.
   The agent can still remove the repeated work around it. */
int main() {
    int n;
    scanf("%d", &n);

    int a = n * 4 + 10;
    int b = n * 4 + 10;           /* same expression computed twice */
    int scale = 2 + 6;            /* constant */
    int wasted = a - a;           /* always 0, never used */

    int total = (a + b) * scale;
    printf("%d\n", total);
    return 0;
}
