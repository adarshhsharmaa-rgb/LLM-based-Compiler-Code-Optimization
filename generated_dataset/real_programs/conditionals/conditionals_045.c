// category: conditionals  (real program 045)
// Codeforces submission 20939819, problem 620/A, GNU C, 2016-09-27
// https://codeforces.com/contest/620/submission/20939819
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<stdio.h>
int main()
{
	int a,b,c,d,q,w;
	scanf("%d %d",&a,&b);
	scanf("%d %d",&c,&d);
	q=c-a;
	if(q<0)
		q=q*(-1);
	w=d-b;
	if(w<0)
		w=w*(-1);
	if(q>w)
		printf("%d",q);
	else
		printf("%d",w);
}
