// category: mixed  (real program 021)
// Codeforces submission 31654426, problem 877/C, GNU C++11, 2017-10-23
// https://codeforces.com/contest/877/submission/31654426
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<stdio.h>
#include<stdlib.h>
#include<string.h>
int main()
{
	int n;
	scanf("%d", &n);
	printf("%d\n", n+n/2);
	for(int i=2; i<=n;i+=2)
		printf("%d ", i);
	for(int i=1; i<=n; i+=2)
		if(i<=n-2)
			printf("%d ", i);
		else
			printf("%d", i);
	for(int i=2; i<=n;i+=2)
		printf(" %d", i);
	printf("\n");
	

}
