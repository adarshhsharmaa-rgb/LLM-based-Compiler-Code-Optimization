// category: loops  (real program 067)
// Codeforces submission 11717040, problem 552/B, GNU C++, 2015-06-23
// https://codeforces.com/contest/552/submission/11717040
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<stdio.h>

int main()
{
	long long n,z=9,c=1,dap=0;
	scanf("%lld",&n);
	while(n>z)
	{
		n-=z;
		dap+=c*z;
		z*=10;
		c++;
	}
	dap += c*n;
	printf("%lld",dap);
}
