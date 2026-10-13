// category: conditionals  (real program 039)
// Codeforces submission 44806646, problem 1068/A, C++14 (GCC 6-32), 2018-10-24
// https://codeforces.com/contest/1068/submission/44806646
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<bits/stdc++.h>
using namespace std;

int main() 
{
    long long n,m,k,l;
    scanf("%lld %lld %lld %lld",&n,&m,&k,&l);
	if(m > n)
		puts("-1");
	else
	{
		long long x = (l+k+m-1)/m;
		if(x*m > n)
			puts("-1");
		else
			printf("%lld\n",x);
	
	}

	return 0;
}
