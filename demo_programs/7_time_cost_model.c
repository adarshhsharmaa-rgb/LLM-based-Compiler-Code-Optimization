#include <stdio.h>

/* Two cost models: run it once as it is, and once with --cost-model time. */
int main() {
    int n;
    scanf("%d", &n);

    int total = 0;
    for (int i = 0; i < 20; i++) {
        int doubled = n * 2;
        total = total + doubled;
    }
    printf("%d\n", total);
    return 0;
}
