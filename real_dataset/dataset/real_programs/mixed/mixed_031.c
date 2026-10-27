// category: mixed  (real program 031)
// Codeforces submission 20295004, problem 656/A, GNU C11, 2016-08-31
// https://codeforces.com/contest/656/submission/20295004
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<stdio.h>

#include<math.h>

int main()

{

	long long int n,i;

	scanf("%lld",&n);

	long long int g=1;

	for(i=1;i<=n;i++)

	{

		g=g*2;

		if(i==13)

		{

			g=8092;

		}

	}

	printf("%I64d\n",g);

}
