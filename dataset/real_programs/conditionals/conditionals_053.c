// category: conditionals  (real program 053)
// Codeforces submission 4142430, problem 40/B, GNU C++, 2013-07-23
// https://codeforces.com/contest/40/submission/4142430
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include <stdio.h>

int main()
{
	int n, m, x;
	scanf(" %d %d %d", &n, &m, &x);
	
	int k = n+m-2-4*(x-1);
	if((n+1)/2 < x || (m+1)/2 < x)
		printf("0");
	else if(x > 100000)
		printf("0");
	else if(k==0)
		printf("1");
	else if(k < 0)
		printf("0");
	else
		printf("%d", k);
	
	return 0;
}
