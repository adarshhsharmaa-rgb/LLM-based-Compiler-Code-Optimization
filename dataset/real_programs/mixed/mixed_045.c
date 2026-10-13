// category: mixed  (real program 045)
// Codeforces submission 31083516, problem 869/B, C++14 (GCC 6-32), 2017-10-06
// https://codeforces.com/contest/869/submission/31083516
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include <cstdio>
#include <cmath>
#include <cstring>
using namespace std;
long long a,b;
main()
{
	scanf("%lld%lld",&a,&b);
	long long temp=b-a;
	if (temp>9)
		puts("0");
	else
	{
		long long ans=1;
		for (long long i=a+1;i<=b;i++)
		{
			int now=i%10;
			ans=ans*now%10;
		 } 
		 printf("%d\n",ans);
	}
 }
