// category: dead_code  (real program 056)
// Codeforces submission 18132262, problem 579/A, GNU C, 2016-05-28
// https://codeforces.com/contest/579/submission/18132262
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<stdio.h>

int main()

{

	long long int n,t=0,p=0;

	scanf("%I64d",&n);

	while(n)

	{

		p=p+n%2;

		n=n/2;

	}

	printf("%I64d",p);

}
