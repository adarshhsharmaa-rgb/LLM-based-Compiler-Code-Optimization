// category: conditionals  (real program 079)
// Codeforces submission 21792261, problem 610/A, GNU C, 2016-10-26
// https://codeforces.com/contest/610/submission/21792261
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<stdio.h>
#include<string.h>
int main()
{
	long int n;
	scanf("%ld",&n);
	if(n%2==1)
		printf("0");
	else if(n==4)
		printf("0");
	else
		printf("%ld",((((n-2)/2)-2)/2)+1);
	return 0;
}
