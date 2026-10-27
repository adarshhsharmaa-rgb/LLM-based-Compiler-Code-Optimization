// category: mixed  (real program 046)
// Codeforces submission 22233970, problem 734/B, GNU C++, 2016-11-15
// https://codeforces.com/contest/734/submission/22233970
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include <stdio.h>

using namespace std;
int k2, k3, k5, k6, ok = 0;
long long s = 0;

int main()
{
    scanf ("%d%d%d%d", &k2, &k3, &k5, &k6);
    while (ok == 0) {
        if (k2 > 0 && k5 > 0 && k6 > 0) {
            s += 256;
            --k2;
            --k5;
            --k6;
        }
        else
            ok = 1;
    }
    ok = 0;
    while (ok == 0) {
        if (k3 > 0 && k2 > 0) {
            s += 32;
            --k3;
            --k2;
        }
        else
            ok = 1;
    }

    printf ("%d", s);

    return 0;
}
