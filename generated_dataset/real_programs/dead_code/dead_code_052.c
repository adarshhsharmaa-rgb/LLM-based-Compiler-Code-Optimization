// category: dead_code  (real program 052)
// Codeforces submission 17940815, problem 675/B, GNU C++, 2016-05-16
// https://codeforces.com/contest/675/submission/17940815
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<bits/stdc++.h>
using namespace std;
typedef long long ll;
#define pb push_back
#define mp make_pair
#define MOD 1000000007
#define PI 3.1415926535897932
#define inf 10000000000000
int main()
{   
	ll n,a,b,c,d,ans,e,f,g,h;
	scanf("%lld%lld%lld%lld%lld",&n,&a,&b,&c,&d);
	ans=n;
	ll count=0;
	for(f=1;f<=n;f++)
	{
		e=c-b+f;
		h=a-d+f;
		g=c-b+a-d+f;
		if(e>=1ll&&e<=n&&h>=1ll&&h<=n&&g>=1ll&&g<=n)
		count++;
	}
	count=count*n;
	printf("%lld\n",count);
	return 0;
}
