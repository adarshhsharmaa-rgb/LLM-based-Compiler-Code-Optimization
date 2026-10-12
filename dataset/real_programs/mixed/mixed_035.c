// category: mixed  (real program 035)
// Codeforces submission 35631189, problem 940/B, C++14 (GCC 6-32), 2018-02-24
// https://codeforces.com/contest/940/submission/35631189
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include <bits/stdc++.h>

typedef unsigned long long ull;
typedef long long ll;
typedef unsigned int ui;

int main() {
    ui n, k, a, b;
    scanf("%d %d %d %d", &n, &k, &a, &b);
    ull sum = 0;
    while (n > 1) {
        ui r = n % k;
        if (k > 1 && !r) {
            ui m = n / k;
            ull ad = 1ULL * (n - m) * a;
            n = m;
            if (ad >= b) {
                sum += b;
            } else {
                sum += ad;
            }
        } else {
            if(n <= k || r == 0) {
                r = n - 1;
            }
            n -= r;
            sum += 1ULL * r * a;
        }
    }
    printf("%llu", sum);
    return 0;
}
