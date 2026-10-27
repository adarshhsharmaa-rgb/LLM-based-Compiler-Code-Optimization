// category: dead_code  (real program 046)
// Codeforces submission 31084138, problem 869/B, GNU C++11, 2017-10-06
// https://codeforces.com/contest/869/submission/31084138
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<bits/stdc++.h>

using namespace std;

typedef long long ll;
const int inf = 0x3f3f3f3f;
const int maxn = 20000000+10;

int main()
{
    ll a,b;
    scanf("%I64d%I64d",&a,&b);
    if(a%10==0)
    {
        if(b>=a+10) printf("0\n");
        else
        {
            ll base=1;
            ll ttt=b%10;
            ll t=a%10;
            for(ll i=t+1;i<=ttt;i++) base*=i;
            printf("%d\n",base%10);
        }
    }
    else
    {
        ll t=a%10;
        ll tt=a-t+10;
        ll ttt=b%10;
        if(tt>a&&tt<=b) printf("0\n");
        else
        {
            ll base=1;
            for(ll i=t+1;i<=ttt;i++) base*=i;
            printf("%d\n",base%10);
        }
    }
    return 0;
}
