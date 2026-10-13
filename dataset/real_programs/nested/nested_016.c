// category: nested  (real program 016)
// Codeforces submission 16628528, problem 630/H, GNU C++, 2016-03-10
// https://codeforces.com/contest/630/submission/16628528
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<stdio.h>
typedef long long ll;
int main()
{
    ll n;
    scanf("%I64d",&n);
    ll a=n*(n-1)*(n-2)*(n-3)*(n-4)/120;
    printf("%I64d\n",a*a*120);
}
