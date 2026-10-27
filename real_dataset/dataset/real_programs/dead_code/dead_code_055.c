// category: dead_code  (real program 055)
// Codeforces submission 22964618, problem 743/C, C++14 (GCC 6-32), 2016-12-14
// https://codeforces.com/contest/743/submission/22964618
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include <bits/stdc++.h>
using namespace std;

#define N 200008
#define LL long long
#define clr(x,v) memset(x,v,sizeof(x));
#define bitcnt(x) __builtin_popcount(x)
#define rep(x,y,z) for (int x=y;x<=z;x++)
#define repd(x,y,z) for (int x=y;x>=z;x--)
const int mo  = 1000000007;
const int INF = 2000000000;
/**************************************************************************/
int n;

int main()
{
	scanf("%d",&n);
	if (n==1) printf("-1\n"); else
	printf("%d %d %d\n",n,n+1,n*(n+1));
}
