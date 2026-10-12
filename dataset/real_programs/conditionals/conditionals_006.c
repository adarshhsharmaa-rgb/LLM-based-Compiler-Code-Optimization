// category: conditionals  (real program 006)
// Codeforces submission 15592476, problem 387/A, GNU C++, 2016-01-26
// https://codeforces.com/contest/387/submission/15592476
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<stdio.h>
int main()
{
	int a,b,c,d,e,f;
	scanf("%d:%d",&a,&b);
	scanf("%d:%d",&c,&d);
	e=a-c;
	f=b-d;
	if(f<0){
		f=f+60;
		e=e-1;
	}
	if(e<0) e=e+24;
	printf("%02d:%02d",e,f);
	return 0;
}
