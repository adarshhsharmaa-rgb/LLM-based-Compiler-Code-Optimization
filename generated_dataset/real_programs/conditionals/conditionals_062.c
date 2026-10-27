// category: conditionals  (real program 062)
// Codeforces submission 30155781, problem 854/B, C++14 (GCC 6-32), 2017-09-06
// https://codeforces.com/contest/854/submission/30155781
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<iostream>
#include<stdio.h>
#include<cstring>
#include<algorithm>
using namespace std;
long long n,k;
int main()
{
	scanf("%I64d%I64d",&n,&k);
	if (k==0) 
	{
		printf("0 0\n"); return 0;
	}
	if (k==n) 
	{
		printf("0 0\n"); return 0;
	}
	printf("1 ");
	if (k*3<=n)
	{
		printf("%I64d\n",2*k);
	}
	else
	printf("%I64d\n",n-k);
}
