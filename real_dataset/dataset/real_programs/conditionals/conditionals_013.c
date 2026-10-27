// category: conditionals  (real program 013)
// Codeforces submission 5897812, problem 382/B, GNU C++, 2014-02-04
// https://codeforces.com/contest/382/submission/5897812
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include <cstdio>
long long a, b, w, x, c;
int main() {
    long long p;
    scanf("%I64d%I64d%I64d%I64d%I64d", &a, &b, &w, &x, &c);
    if (a >= c) {puts("0"); return 0; }
    p = (c * x - a * x - b + w - x - 1) / (w - x);
    printf("%I64d\n", c - a + p);
}
