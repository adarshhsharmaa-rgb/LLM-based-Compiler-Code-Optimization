// category: repeated_expr  (real program 014)
// Codeforces submission 44808364, problem 1068/B, C++14 (GCC 6-32), 2018-10-24
// https://codeforces.com/contest/1068/submission/44808364
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include <bits/stdc++.h>

using namespace std;

int main(){
    //freopen("00.txt", "r", stdin);
    long long n, i, j, ans = 0;

    scanf("%lld", &n);
    for( i = 1; i*i<=n; i++ ){
        if( i*i == n ){
            ans++;
        }
        else if( n%i == 0 ){
            ans += 2ll;
        }
    }
    printf("%lld\n", ans);

    return 0;
}
