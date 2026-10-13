// category: arithmetic  (real program 037)
// Codeforces submission 39618947, problem 996/A, GNU C11, 2018-06-24
// https://codeforces.com/contest/996/submission/39618947
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<stdio.h>
int main()
{
	int n;
	scanf("%d",&n);
	int x,c=0;
	x=n;
		c=x/100;
		x=x%100;
		c=c+x/20;
		x=x%20;
		c=c+x/10;
		x=x%10;
		c=c+x/5;
		x=x%5;
		c=c+x/1;
		x=x%1;
	printf("%d",c);
}
