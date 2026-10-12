// category: conditionals  (real program 065)
// Codeforces submission 31568931, problem 883/M, GNU C, 2017-10-21
// https://codeforces.com/contest/883/submission/31568931
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include <stdio.h>
int main()
{
	int a,b,c,d;
	scanf("%d%d%d%d",&a,&b,&c,&d);
	
		int x=a-c;
		if(x<0)
			x=x*-1;
		x=2*x;
		if(x==0)
			x=4;
		else
			x=x+2;
		int y=d-b;
		if(y<0)
			y=y*-1;
		y=2*y;
		if(y==0)
			y=4;
		else
			y=y+2;
		printf("%d\n",(x+y));

	
	return 0;
}
