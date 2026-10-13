// category: nested  (real program 003)
// Codeforces submission 22088019, problem 268/B, C++14 (GCC 6-32), 2016-11-07
// https://codeforces.com/contest/268/submission/22088019
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<bits/stdc++.h>

using namespace std;

int main(){

    long long int n;

    scanf("%lld",&n);

    long long int ans;

    ans = (n*n*n + 5*n)/6;

    printf("%lld",ans);

}
