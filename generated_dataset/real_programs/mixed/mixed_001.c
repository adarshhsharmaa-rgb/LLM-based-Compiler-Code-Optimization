// category: mixed  (real program 001)
// Codeforces submission 31573297, problem 883/M, GNU C11, 2017-10-21
// https://codeforces.com/contest/883/submission/31573297
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<stdio.h>
#include<math.h>
int main()
{ int x1,x2,y1,y2,dai,rong,i;
	scanf("%d %d",&x1,&y1);
	scanf("%d %d",&x2,&y2);
	dai=0;rong=0;
	if(x1<x2)
	for(i=x1;i<=x2;i++)
	dai++; else
	if(x2<x1)
		for(i=x2;i<=x1;i++)
	dai++;
	if(y1<y2)
	for(i=y1;i<=y2;i++)
	rong++;else 
	if(y2<y1)
	for(i=y2;i<=y1;i++)
	rong++;
	if(x1==x2) dai+=2;
	if(y1==y2) rong+=2;
	printf("%d",dai*2+rong*2);
		
	
}
