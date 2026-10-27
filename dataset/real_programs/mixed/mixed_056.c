// category: mixed  (real program 056)
// Codeforces submission 11411451, problem 11/B, GNU C++, 2015-06-04
// https://codeforces.com/contest/11/submission/11411451
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include <stdio.h>

int main()
{
	int x,i,sum=0;
	scanf("%d",&x);
	if(x<0) x=-x;
	for(i=0;sum<x || (sum%2) != (x%2);sum+=i)
		i++;
	printf("%d\n",i);
	return 0;
}
