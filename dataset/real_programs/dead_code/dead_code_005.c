// category: dead_code  (real program 005)
// Codeforces submission 660224, problem 112/B, GNU C++, 2011-09-03
// https://codeforces.com/contest/112/submission/660224
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include <cstdio>
#include <cstring>
#include <algorithm>
using namespace std;
const int maxn = 1000;
int main() {
    int n, x, y;
    scanf("%d%d%d", &n, &x, &y);
    if (n % 2 == 1) printf("NO\n");
    else {
        int a = n / 2;
        int b = n / 2 + 1;
        if ((x == a || x == b) && (y == a || y == b)) printf("NO\n");
        else printf("YES\n");
    }
}
