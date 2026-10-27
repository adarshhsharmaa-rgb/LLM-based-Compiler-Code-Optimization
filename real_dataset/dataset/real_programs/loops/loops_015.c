// category: loops  (real program 015)
// Codeforces submission 3026771, problem 268/C, GNU C++, 2013-01-28
// https://codeforces.com/contest/268/submission/3026771
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include <stdio.h>
#include <algorithm>

using namespace std;

int N, M;
int t;

int main() {
        scanf("%d%d", &N, &M);

        for (int x = N, y = 0; x >= 0 && y <= M; x--, y++) {
                t++;
        }

        printf("%d\n", t);

        for (int x = N, y = 0; x >= 0 && y <= M; x--, y++) {
                printf("%d %d\n", x, y);
        }

        return 0;
}
