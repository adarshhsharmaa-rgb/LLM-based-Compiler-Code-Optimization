// category: conditionals  (real program 055)
// Codeforces submission 2754884, problem 194/A, GNU C++, 2012-12-12
// https://codeforces.com/contest/194/submission/2754884
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<stdio.h>
int main()
{	
	int a,b;
	scanf("%d%d",&a,&b);
	if(3*a<=b)
		printf("0");
	else
	printf("%d",a-(b-2*a));
}
