// category: repeated_expr  (real program 055)
// Codeforces submission 20363554, problem 483/A, C++14 (GCC 6-32), 2016-09-03
// https://codeforces.com/contest/483/submission/20363554
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include <cstdio>

int main() {
    long long l, r;
    scanf("%lld %lld", &l, &r);

    if (l % 2 != 0) l++;
    
    if (l + 2 > r)  printf("-1\n");
    else    printf("%lld %lld %lld\n", l, l + 1, l + 2);

    return 0;
}
