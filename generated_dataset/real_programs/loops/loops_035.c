// category: loops  (real program 035)
// Codeforces submission 17483252, problem 669/A, GNU C++, 2016-04-24
// https://codeforces.com/contest/669/submission/17483252
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include <bits/stdc++.h>

using namespace std;

int main(){
    int n, t=0;

    scanf("%d", &n);

    for (int i=1;i<=n;i++){
        n -= i % 2;
        t++;
    }

    printf("%d\n", t);

    return 0;

}
