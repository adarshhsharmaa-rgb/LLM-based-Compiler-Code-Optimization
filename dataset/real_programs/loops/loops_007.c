// category: loops  (real program 007)
// Codeforces submission 13605238, problem 46/A, GNU C++, 2015-10-14
// https://codeforces.com/contest/46/submission/13605238
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<stdio.h>
int main()
{
	int n,i,t;
	scanf("%d",&n);
	t=2;
	for (i=1;i<=n-1;i++)
	{
		printf("%d ",t);
		t=(t+i)%n+1;
	}
}
