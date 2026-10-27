// category: dead_code  (real program 010)
// Codeforces submission 3023085, problem 268/C, GNU C++, 2013-01-28
// https://codeforces.com/contest/268/submission/3023085
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include <cstdio>
#include <iostream>

using namespace std;

int n, m, x, y;
int i;
int main() {
    scanf("%d%d", &n, &m);
    if(n < m) {
        x = n; y = 0;
        printf("%d\n", n + 1);
        for(i = 0; i <= n; i++) {
            printf("%d %d\n", n - i, i);
        }
    }
    else {
        printf("%d\n", m + 1);
        for(i = 0; i <= m; i++) {
            printf("%d %d\n", i, m - i);
        }
    }
    return 0;
}
