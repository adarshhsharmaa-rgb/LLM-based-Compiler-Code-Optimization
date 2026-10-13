// category: dead_code  (real program 015)
// Codeforces submission 31406414, problem 876/A, C++14 (GCC 6-32), 2017-10-16
// https://codeforces.com/contest/876/submission/31406414
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include <stdio.h>
#include <math.h>

int main()
{
	int n;
	int a,b,c;
	int sum=0;
	scanf("%d",&n);
	scanf("%d %d %d",&a,&b,&c);
	if(n==1)
	{
		printf("0\n");
	}
	else
	{
		if(a<b)
		{
			if(a<=c)
			{
				printf("%d\n",a*(n-1));
				return 0;
			}
			else
			{
				if(c<b)
				{
					printf("%d\n",a+(n-2)*c);
					return 0;
				}
			}
		}
		else
		{
			if(b<=c)
			{
				printf("%d\n",(n-1)*b);
				return 0;
			}
			else
			{
				printf("%d\n",b+(n-2)*c);
				return 0;	
			}
		}
	}	
	return 0;
}
