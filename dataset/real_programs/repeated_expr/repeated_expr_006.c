// category: repeated_expr  (real program 006)
// Codeforces submission 7147626, problem 40/B, GNU C++, 2014-07-18
// https://codeforces.com/contest/40/submission/7147626
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include <cstdio>
typedef long long ll;
int main() {
    ll n, m, x;
    scanf("%I64d%I64d%I64d", &n, &m, &x);
    n -= 2 * (x - 1);
    m -= 2 * (x - 1);
    if (n < 1 || m < 1) puts("0");
    else if (n + m == 2) puts("1");
    else printf("%I64d", n + m - 2);
    return 0;
}
