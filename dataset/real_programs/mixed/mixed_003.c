// category: mixed  (real program 003)
// Codeforces submission 32869654, problem 897/B, MS C++, 2017-12-02
// https://codeforces.com/contest/897/submission/32869654
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include <stdio.h>
#include <stdlib.h>
void main()
{
	long long int ch, i, k, p, s=0, k1, r;
	scanf("%I64d %I64d", &k, &p);
	for(i=1; i<=k; i++)
	{
		k1=i;
		ch=i;
		while(k1>0)
		{
			r=k1%10;
			if(r==0)
				ch=ch*10;
			else
			{
				ch=ch*10;
				ch=ch+r;
			}
			k1=k1/10;
		}
		s=s+ch%p;
	}
	printf("%I64d", s%p);
}
