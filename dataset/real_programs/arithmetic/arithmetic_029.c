// category: arithmetic  (real program 029)
// Codeforces submission 17482872, problem 669/A, GNU C++, 2016-04-24
// https://codeforces.com/contest/669/submission/17482872
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include <bits/stdc++.h>
using namespace std;
#define MAX 5005
#define ll long long


int main()
{
    ll x;
    scanf("%lld", &x);
    ll ans = x / 3 * 2;
    ans += (x % 3 != 0);
    printf("%lld\n", ans);
    
    return 0;
}
