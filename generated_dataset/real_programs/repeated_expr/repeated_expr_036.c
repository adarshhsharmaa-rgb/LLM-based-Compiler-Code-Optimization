// category: repeated_expr  (real program 036)
// Codeforces submission 17949412, problem 675/B, GNU C++, 2016-05-16
// https://codeforces.com/contest/675/submission/17949412
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include <cstdio>
int n, a, b, c, d;
long long s;
int main(){
    scanf("%d%d%d%d%d", &n, &a, &b, &c, &d);
    for (int i = 1; i <= n; i++) {
        if ( (c + ((i + b - c) + a - d) - b) + d == i + a && (i + b - c) > 0 && (i + b - c) <= n &&
             ((i + b - c) + a - d) > 0 && ((i + b - c) + a - d) <= n && (c + ((i + b - c) + a - d) - b) > 0 &&
             (c + ((i + b - c) + a - d) - b) <= n) {
            s++;
        }
    }
    printf("%I64d", s * n);
    return 0;
}
