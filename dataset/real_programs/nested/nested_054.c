// category: nested  (real program 054)
// Codeforces submission 447109, problem 84/A, GNU C, 2011-05-13
// https://codeforces.com/contest/84/submission/447109
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main() {
    int i, n;
    scanf("%d", &n);

    printf("%d", n + n / 2 + n % 2);

    return 0;
}
