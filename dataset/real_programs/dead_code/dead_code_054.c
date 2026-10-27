// category: dead_code  (real program 054)
// Codeforces submission 31657256, problem 877/C, GNU C11, 2017-10-23
// https://codeforces.com/contest/877/submission/31657256
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include <stdio.h>
int main()
{
	int n;
	scanf("%d",&n);
	int m = n+1;
	int count = 0;
	for(int i=1;i<=n;i++)
	{
		if(i%2 == 0)
		{
			count+=2;
		}
		else
		{
			count+=1;
		}
	}
	printf("%d\n",count);
	for(int i = 1;2*i<=n;i++)
	{
		printf("%d ",2*i);
	}
	for(int i = 1;i<=n;i+=2)
	{
		printf("%d ",i);
	}
	for(int i = 1;2*i<=n;i++)
	{
		printf("%d ",2*i);
	}
	return 0;
}
