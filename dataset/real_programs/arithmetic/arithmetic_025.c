// category: arithmetic  (real program 025)
// Codeforces submission 39621292, problem 996/A, GNU C++11, 2018-06-24
// https://codeforces.com/contest/996/submission/39621292
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<bits/stdc++.h>
#define clr(x) memset(x,0,sizeof(x))
#define clr_1(x) memset(x,-1,sizeof(x))
#define INF 0x3f3f3f3f
#define LL long long
#define pb push_back
#define ls(i) (i<<1)
#define rs(i) (i<<1|1)
#define mp make_pair
#define fi first
#define se second
using namespace std;
LL n;
LL ans;
int main()
{
    scanf("%I64d",&n);
    ans+=n/100;
    n%=100;
    ans+=n/20;
    n%=20;
    ans+=n/10;
    n%=10;
    ans+=n/5;
    n%=5;
    ans+=n;
    printf("%I64d\n",ans);
    return 0;
}
