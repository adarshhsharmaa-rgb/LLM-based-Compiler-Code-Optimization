// category: conditionals  (real program 070)
// Codeforces submission 43302284, problem 1030/D, C++14 (GCC 6-32), 2018-09-23
// https://codeforces.com/contest/1030/submission/43302284
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<iostream>
#include<cstdio>
#include<cstring>
#include<algorithm>
using namespace std;
int main()
{
	long long n,m,k;
	scanf("%lld%lld%lld",&n,&m,&k);
	if((1ll*n*m*2)%k==0)
	{
		printf("YES\n");
		long long S=n*m*2/k;
		long long y2=(S-1)/n+1;
		long long x1=n;
		long long y1=1;
		long long x2=(y2*x1-S);
		printf("0 0\n");
		printf("%lld %lld\n",x1,y1);
		printf("%lld %lld\n",x2,y2);
	}
	else
		printf("NO\n");
	return 0;
}
