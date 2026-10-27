// category: dead_code  (real program 043)
// Codeforces submission 16183078, problem 630/H, GNU C++, 2016-02-18
// https://codeforces.com/contest/630/submission/16183078
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<stdio.h>
int n;
unsigned long long sum=1,ans;
int main()
{
	scanf("%d",&n);
  ans=1;
  for (int i=1;i<=5;i++)
  ans*=n-i+1;
	printf("%I64d",ans/120*ans);
	return 0;
}
