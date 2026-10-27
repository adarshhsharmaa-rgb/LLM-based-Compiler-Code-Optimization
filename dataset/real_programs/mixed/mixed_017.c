// category: mixed  (real program 017)
// Codeforces submission 36414307, problem 926/A, GNU C++11, 2018-03-19
// https://codeforces.com/contest/926/submission/36414307
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include <iostream>
#include <cassert>
#define MAX 5

using namespace std;
typedef unsigned long long int ll;
int main()
{
    ll ans = 0;
    ll a,b;

    scanf("%lld %lld",&a,&b);
    ll x_part = 1, y_part = 1;

    for(ll x = 0; x <= 32 && x_part <= b; x++, x_part = x_part * 2){
        y_part = 1;
        for(ll y = 0; y <= 32 && y_part <= b; y++,y_part = y_part*3){
            ll p = x_part * y_part;
            if(p >= a && p <= b)    ans++;

        }
    }
    printf("%lld\n",ans);
}
