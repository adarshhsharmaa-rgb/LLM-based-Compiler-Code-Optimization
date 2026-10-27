// category: mixed  (real program 027)
// Codeforces submission 18655488, problem 90/A, GNU C++11, 2016-06-23
// https://codeforces.com/contest/90/submission/18655488
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include <bits/stdc++.h>
using namespace std;

int r, g, b, ans = 29;
int main() {
    scanf("%d%d%d",&r,&g,&b);
    int curr = 0;
    while(r+g+b>0) {
        if(curr == 0) {
            if(r > 0) r--;
            if(r > 0) r--;
            curr = 1;
        } else if(curr == 1) {
            if(g > 0) g--;
            if(g > 0) g--;
            curr = 2;
        } else if(curr == 2) {
            if(b > 0) b--;
            if(b > 0) b--;
            curr = 0;
        }
        ans++;
    }
    printf("%d", ans);
}
