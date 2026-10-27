// category: loops  (real program 031)
// Codeforces submission 22047019, problem 732/A, GNU C++, 2016-11-05
// https://codeforces.com/contest/732/submission/22047019
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include <cstdio>

int k, n;

int main()
{
    scanf("%d%d", &k, &n); k %= 10;
    int ans = 1, x = k;
    while (x != n && x != 0) { x = (x + k) % 10; ++ans; }
    printf("%d\n", ans);
    return 0;
}
