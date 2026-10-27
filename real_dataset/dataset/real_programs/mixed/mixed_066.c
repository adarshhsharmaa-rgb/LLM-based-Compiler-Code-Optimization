// category: mixed  (real program 066)
// Codeforces submission 25522498, problem 785/C, MS C++, 2017-03-15
// https://codeforces.com/contest/785/submission/25522498
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include <cstdio>

int main()
{
    long long n, m;
    scanf("%I64d%I64d", &n, &m);
    if (m >= n) {
        printf("%I64d\n", n);
        return 0;
    }
    n -= m;
    n = n * 2LL;
    long long a = 1LL, b = 2000000000LL;
    while (a < b) {
        long long q = (a + b) / 2LL;
        if (q * q + q < n)
            a = q + 1;
        else
            b = q;
    }
    printf("%I64d\n", a + m);
    return 0;
}
