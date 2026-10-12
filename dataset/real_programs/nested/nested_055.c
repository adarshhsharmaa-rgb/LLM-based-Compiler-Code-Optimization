// category: nested  (real program 055)
// Codeforces submission 16218464, problem 630/H, GNU C++, 2016-02-20
// https://codeforces.com/contest/630/submission/16218464
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<stdio.h>

int main()
{
	__int64 n,r;
	scanf("%I64d",&n);
	r=n*(n-1)/2*(n-2)/3*(n-3)/4*(n-4)/5;
	printf("%I64d\n",r*r*120);
	return 0;
}
