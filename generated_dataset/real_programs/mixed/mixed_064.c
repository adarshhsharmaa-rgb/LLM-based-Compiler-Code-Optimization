// category: mixed  (real program 064)
// Codeforces submission 26015191, problem 784/B, C++14 (GCC 6-32), 2017-03-31
// https://codeforces.com/contest/784/submission/26015191
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include <bits/stdc++.h>
using namespace std;

int main() {
    int n;
    int res = 0;
    scanf("%d", &n);
    if (n == 0) {
        res = 1;
    } else {
        while (n > 0) {
            int val = n % 16;
            if (val == 0 || val == 4 || val == 6 || val == 8 || val == 9 || val == 10 || val == 11 || val == 13) {            
                res++;
            }
            if (val == 8 || val == 11) {
                res++;
            }
            n /= 16;
        }
    }

    printf("%d\n", res);
    return 0;
}


//0123456789ABCDEF
