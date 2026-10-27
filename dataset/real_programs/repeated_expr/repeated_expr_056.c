// category: repeated_expr  (real program 056)
// Codeforces submission 47423555, problem 1085/B, C++14 (GCC 6-32), 2018-12-23
// https://codeforces.com/contest/1085/submission/47423555
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include <bits/stdc++.h>
using namespace std;
typedef long long ll;
int main() {
	ll n, k, i, j;
	scanf("%lld %lld", &n, &k);
	if(n>=k)
	{
		//maximum remainder can be k-1;
		for(i=k-1; i>0; i--)
		{
			if(n%i==0)
			{
				j=i;
				while(1)
				{
					if(((j/k)*(i))==n)
					{
						printf("%lld\n", j);
						return 0;
					}
					j+=k;
				}
			}
		}
	}
	else if(n<k)
	{
		for(i=n; i>0; i--)
		{
			if(n%i==0)
			{
				j=i;
				while(1)
				{
					if(((j/k)*(i))==n)
					{
						printf("%lld\n", j);
						return 0;
					}
					j+=k;
				}
			}
		}
	}
	return 0;
}
