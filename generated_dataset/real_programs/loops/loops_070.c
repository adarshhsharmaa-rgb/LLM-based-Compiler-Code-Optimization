// category: loops  (real program 070)
// Codeforces submission 32871909, problem 897/B, GNU C++11, 2017-12-02
// https://codeforces.com/contest/897/submission/32871909
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
//by ��ά
#include<iostream>
#include<cstdio>
#include<cstring>
#include<queue>
#include<bitset>
#include<set>
#include<cmath>
#include<vector>
#include<set>
#include<map>
#include<ctime>
#include<algorithm>
#define ll long long
#define inf 1<<30
using namespace std;

ll k,p;
ll ans;

int main()
{
	scanf("%I64d%I64d",&k,&p);
	for(ll i=1;i<=k;++i)
	{
		ll x=i,y=i;
		while(x){
			y=(y*10+x%10)%p;
			x/=10;
		}
		ans=(ans+y)%p;
	}
	printf("%I64d",ans);
	return 0;
}
