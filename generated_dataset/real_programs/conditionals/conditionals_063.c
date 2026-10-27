// category: conditionals  (real program 063)
// Codeforces submission 45300894, problem 1075/A, C++14 (GCC 6-32), 2018-11-04
// https://codeforces.com/contest/1075/submission/45300894
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<stdio.h>

int main()
{
	long long int n,x,y,p=0,q=0;
	scanf("%lli", &n);
	scanf("%lli%lli", &x,&y);
	p=(x-1)+(y-1);
	q=(n-x)+(n-y);
	if(p==q)
	printf("White\n");
	if(p>q)
	printf("Black\n");
	if(p<q)
	printf("White\n");
	return 0;
}
