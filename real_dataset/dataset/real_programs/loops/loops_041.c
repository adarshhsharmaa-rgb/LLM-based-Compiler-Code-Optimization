// category: loops  (real program 041)
// Codeforces submission 15495330, problem 171/A, GNU C++, 2016-01-22
// https://codeforces.com/contest/171/submission/15495330
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include <stdio.h>
int x,y,z;
int main()
{
	scanf("%d%d",&x,&y);
	while(y)
	{
		z=z*10+y%10;
		y=y/10;
	}
	printf("%d",z+x);
	return 0;
}
