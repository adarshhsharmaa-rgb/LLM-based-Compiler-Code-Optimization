// category: repeated_expr  (real program 002)
// Codeforces submission 272457, problem 18/B, GNU C++, 2011-02-01
// https://codeforces.com/contest/18/submission/272457
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<cstdio>
typedef long long ll;
int main()
{
    ll n,d,m,l;
    scanf("%I64d%I64d%I64d%I64d",&n,&d,&m,&l);
    for(ll k=0;k<n;k++)
    {
        ll x=((k*m+l)/d+1)*d;
        if(k<n-1&&x<k*m+m||k==n-1)
        {
            printf("%I64d\n",x);
            return 0;
        }
    }
}
