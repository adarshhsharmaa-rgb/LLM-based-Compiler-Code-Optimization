// category: mixed  (real program 040)
// Codeforces submission 13218583, problem 378/A, GNU C++, 2015-09-25
// https://codeforces.com/contest/378/submission/13218583
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<stdio.h>

int main()
{
	int a,b,p,q,x=0,y=0,z=0;
	scanf("%d%d",&a,&b);
	int i,j;
	for(i=1;i<=6;i++)
	{
		p=a-i;
		q=b-i;
		if(p<0)p=-p;
		if(q<0)q=-q;
		if(p>q)x++;
		else if(p==q)y++;
		else z++;
	}
	printf("%d %d %d",z,y,x);
	return 0;
}
