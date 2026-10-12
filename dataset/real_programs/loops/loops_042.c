// category: loops  (real program 042)
// Codeforces submission 16610498, problem 630/H, GNU C++, 2016-03-09
// https://codeforces.com/contest/630/submission/16610498
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
//H
#include<cstdio>
int main()
{
	int n,j;
	long long m,temp;
	scanf("%d",&n);
	temp=1;
	for(j=1;j<=5;j++) 
		temp=temp*(n-j+1)/j;
	m=temp*temp*120;
	printf("%lld\n",m);
}
