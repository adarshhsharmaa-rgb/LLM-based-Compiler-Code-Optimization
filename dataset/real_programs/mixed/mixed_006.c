// category: mixed  (real program 006)
// Codeforces submission 44293143, problem 1064/A, GNU C++11, 2018-10-14
// https://codeforces.com/contest/1064/submission/44293143
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include <algorithm>
#include <iostream>
#include <cstring>
#include <cstdlib>
#include <cctype>
#include <cstdio>
using namespace std;

int a, b, c, ans;

int main() {
    scanf("%d%d%d", &a, &b, &c);
    int cur = 233, num = 0;
    while((a + b <= c) || (b + c <= a) || (a + c <= b)) {
        cur = 233;
        if(a > b) {
            cur = b;
            num = 2;
        }
        if(a < cur) {
            cur = a;
            num = 1;
        }
        if(c < cur) {
            cur = c;
            num = 3;
        }
        if(num == 1) ++a;
        else if(num == 2) ++b;
        else if(num == 3) ++c;
        ++ans;
    }
    printf("%d\n", ans);
    return 0;
}
