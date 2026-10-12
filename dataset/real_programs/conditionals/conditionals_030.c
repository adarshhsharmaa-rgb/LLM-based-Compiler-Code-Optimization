// category: conditionals  (real program 030)
// Codeforces submission 7167431, problem 450/B, GNU C++, 2014-07-19
// https://codeforces.com/contest/450/submission/7167431
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include <stdio.h>
#include <string.h>
#include <math.h>
#include <algorithm>
#include <string>
#include <vector>
#include <queue>
#include <map>
#include <stack>
#include <deque>
#define INF ((int)1e8)

using namespace std;




int main() {
    int a, b, n;
    scanf("%d %d", &a, &b);
    scanf("%d", &n);
    int ans = 0;
    int val = n%6;
    /*switch(val) {
        case 0: ans = a - b;
        case 1: ans = a;
        case 2: ans = b;
        case 3: ans = b - a;
        case 4: ans = -a;
        case 5: ans = -b;
    }*/
    if (val == 0) ans = a - b;
    if (val == 1) ans = a;
    if (val == 2) ans = b;
    if (val == 3) ans = b - a;
    if (val == 4) ans = -a;
    if (val == 5) ans = -b;
    //printf("val %d\n %d %d\n", val, a, b);
    /*for (int i = 1; i <= 20; i++) {
        printf("%d %d\n", i, recur(i));
    }*/
    printf("%d\n", ((ans%1000000007)+1000000007)%1000000007);
}
